import json
import logging
import time
from threading import Thread

from django.core.exceptions import PermissionDenied
from django.forms import model_to_dict
from django.utils import timezone
from django.db import IntegrityError
from requests import ConnectTimeout, HTTPError, request

from common.models.event import Event
from fpl.exceptions.fpl_data_exceptions import FplPlayerDataError, \
    PlayerHistoryError
from fpl.properties.properties import check_player_history_required, \
    get_properties
from players.models import ElementType, Player, PlayerHistory, PlayerStatus
from players.models.player_scout_risk import PlayerScoutRisk
from teams.models import Team
from utils.custom_requests import CustomSession
from utils.json_utils import formatted_json
from utils.model_utils import validate_json_against_model

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

properties = get_properties()


def save_players(data, result_queue):
    """ Parse and save Player data

    :param data: downloaded raw data
    """
    logger.info('Got %s players', str(len(data['elements'])))
    data = validate_json_against_model(data['elements'], Player)

    save_players_by_team(data, result_queue)


def save_player_status(data):
    # Get a distinct list of status'. We have to specify order_by as Player model has implicit ordering,
    # and otherwise that affects the results
    distinct_statuses = Player.objects.order_by().values_list('status', flat=True).distinct()

    for status in distinct_statuses:
        PlayerStatus.objects.update_or_create(
            status=status,
            defaults={'last_updated': timezone.now()}
        )


def save_players_by_team(data, result_queue):
    # Group by team
    grouped_players = {}
    for player in data:
        if player.team not in grouped_players:
            grouped_players[player.team] = []
        grouped_players[player.team].append(player)

    threads = []
    for team, players in grouped_players.items():
        # Create and start a thread for each team's players
        logger.info("Saving players for team %s", Team.objects.get(pk=team).name)
        thread = Thread(target=save_multi_players, args=(Team.objects.get(pk=team), players, result_queue))
        thread.start()
        threads.append(thread)

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    logger.info('Saving player status')
    save_player_status(data)

    # Check for any exceptions raised in the threads
    if not result_queue.empty():
        logger.info('Failed to save some players.')
        raise FplPlayerDataError
    else:
        logger.info('All players saved.')


def save_multi_players(team, players, result_queue):
    max_retry_attempts = properties.retry_attempts
    retry_attempts = 0

    def process_player(player):
        try:
            # Prepare player data with team and type
            player.player_team = Team.objects.get(pk=player.team)
            player.player_type = ElementType.objects.get(pk=player.element_type)

            # value added per million
            player.vapm = player.points_value_added_per_m()

            # Get the history and set it
            time.sleep(properties.request_delay)
            histories = get_player_history(player)
            player.history_last_updated = timezone.now()

            scout_risks = player._extra_fields["scout_risks"]

            player.save()

            # Are there scout risks?
            PlayerScoutRisk.objects.filter(player=player).delete()
            for scout_risk in scout_risks:
                try:
                    gameweek = Event.objects.get(id=scout_risk["gameweek"])
                except Event.DoesNotExist:
                    logger.info(f"Event {scout_risk.gameweek} not found for scout risk on {player.web_name}")
                    continue

                PlayerScoutRisk.objects.create(
                    player=player,
                    gameweek=gameweek,
                    property=scout_risk["property"],
                    notes=scout_risk["notes"],
                    url=scout_risk["url"]
                )


            for history in histories:

                history.last_updated = timezone.now()
                history_data = model_to_dict(history, exclude=['id', 'element', 'fixture', 'player', 'opponent'])  # Exclude fields as needed

                # Try updating or creating the player history
                PlayerHistory.objects.update_or_create(
                    fixture=history.fixture,
                    element=history.element,
                    defaults={
                        'player': Player.objects.get(id=history.element),
                        'opponent': Team.objects.get(id=history.opponent_team),
                        **history_data
                    }
                )

        except Exception as exc:
            logger.info(f"Exception for {player.web_name} ({team.short_name}): {exc}")
            return False
        except IntegrityError as exc:
            logger.info(f"Integrity error for {player.web_name} ({team.short_name}): {exc}")
        return True

    try:
        failed_players = []
        # Loop through all players. This can get updated with failed players later
        while players and retry_attempts < max_retry_attempts:
            for player in players:
                if not process_player(player):
                    # If for any reason a player failed, add it to a list to retry
                    failed_players.append(player)

            players = failed_players
            if failed_players:
                logger.info(f"Got {len(failed_players)} failed players for {team.name}, retrying attempt {retry_attempts + 1}")
            failed_players = []
            retry_attempts += 1

        # If we still have players, after max_retry_attempts, log it and raise an exception
        if players:
            logger.info(f"Failures for {team.name}, exceeded max retries")
            raise FplPlayerDataError

    except Exception as e:
        result_queue.put((team.name, e))
        logger.info("We tried %s times, but still got failed retrieval for players for %s", retry_attempts, team.name)


def get_player_history(player):
    """ Get the players history, and apply their team to the history object

    :param player: this player as an object
    :return: the players history as a list of objects
    """

    updated_history = []
    custom_session = CustomSession(request)

    if check_player_history_required(properties.reload_full_cache_time, player):

        try:
            response = custom_session.custom_request('GET',
                                                     properties.base_url +
                                                     properties.player_url.format(player.id),
                                                     timeout=properties.request_timeout)

            data = formatted_json(response.text)

            data = validate_json_against_model(data['history'], PlayerHistory)
            for history in data:
                updated_history.append(history)

        except (ConnectTimeout, HTTPError, PermissionDenied) as exc:
            logger.info(exc)
            raise PlayerHistoryError from exc

    return updated_history
