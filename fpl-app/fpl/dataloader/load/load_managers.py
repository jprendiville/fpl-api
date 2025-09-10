""" This module is used to do all things around a Manager.

Function are:
parse_and_save_history
parse_and_save_manager
parse_and_save_picks
parse_and_save_manager_information
parse_and_save_manager_standings
get_or_save_manager_team
get_league_standings
check_manager_exists
check_manager_needs_updating
"""

import json
import logging
from datetime import datetime, timedelta, timezone

from dateutil import tz
from django.db.models import Q, Subquery
from django.core.exceptions import PermissionDenied
from requests import RequestException,  request

from common.models.last_updated import LastUpdated
from common.utils import get_current_gameweek
from fpl.enums.common_enums import DataTypeIdentifier
from fpl.exceptions.manager_exceptions import ManagerNotFoundError, \
    PickNotFoundError
from fpl.properties.properties import check_update_required, get_properties
from manager.models import ClassicLeague, ClassicLeagueLiveStandings, \
    ClassicLeaguePhase, \
    ClassicLeagueStandings, History, \
    Information, ManagerTeam, \
    Pick
from players.models import ElementType, Player
from utils.custom_requests import CustomSession
from utils.json_utils import formatted_json
from utils.model_utils import validate_json_against_model

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

properties = get_properties()


def parse_and_save_history(manager, manager_data):
    """ Parse and save manager history

    Get the managers history
    :param manager: manager object
    :param manager_data: raw manager data
    """
    history = History(**manager_data.get('entry_history'))
    history.manager = manager
    history.id = get_manager_history_id(history)
    History.save(history)


def parse_and_save_manager(manager_id, this_gameweek, manager_data):
    """ Parse and save manager

    Get the manager by id
    :param manager_id: manager id as an integer
    :param this_gameweek: this gameweek as an integer
    :param manager_data: raw manager data
    :return: a manager object
    """

    manager = ManagerTeam()
    manager.id = manager_id
    manager.active_chip = manager_data.get('active_chip') or ""
    manager.last_updated_gameweek = this_gameweek.id
    manager.last_update_timestamp = datetime.now(tz.UTC)
    ManagerTeam.save(manager)

    return manager


def parse_and_save_picks(manager, manager_data, this_gameweek):
    """ Parse and save manager picks

    Get the managers picks and save it to the database
    :param manager: manager object
    :param manager_data: raw manager data
    :return:
    """

    picks = [Pick(**data_dict) for data_dict in manager_data['picks']]
    for pick in picks:
        try:
            pick.player = Player.objects.get(pk=pick.element)
            pick.gameweek = this_gameweek.id
            pick.manager = manager
            pick.id = get_manager_pick_id(pick)
            pick.player_type = ElementType.objects.get(pk=pick.player.element_type)
            pick.save()
        except Exception as e:
            logger.exception(f"Error while saving pick: {pick}. Exception: {e}")
            raise PickNotFoundError()

def parse_and_save_manager_information(manager, manager_information):
    """ Parse and save manager information

    Get the managers information and leagues and save it to the database
    The incoming JSON contains some details we don't want so we'll
    construct the manager_information_data manually
    :param manager: manager object
    :param manager_information: raw manager information data
    """
    manager_information_data = {
        'id': manager_information['id'],
        'joined_time': manager_information['joined_time'],
        'started_event': manager_information['started_event'],
        'favourite_team': manager_information['favourite_team'],
        'player_first_name': manager_information['player_first_name'],
        'player_last_name': manager_information['player_last_name'],
        'player_region_id': manager_information['player_region_id'],
        'player_region_name': manager_information['player_region_name'],
        'player_region_iso_code_short':
            manager_information['player_region_iso_code_short'],
        'player_region_iso_code_long':
            manager_information['player_region_iso_code_long'],
        'summary_overall_points':
            manager_information['summary_overall_points'],
        'summary_overall_rank': manager_information['summary_overall_rank'],
        'summary_event_points': manager_information['summary_event_points'],
        'summary_event_rank': manager_information['summary_event_rank'],
        'current_event': manager_information['current_event'],
        'name': manager_information['name'],
        'name_change_blocked': manager_information['name_change_blocked'],
        'kit': manager_information['kit'][:255] if manager_information['kit'] is not None else '',
        'last_deadline_bank': manager_information['last_deadline_bank'],
        'last_deadline_value': manager_information['last_deadline_value'],
        'last_deadline_total_transfers':
            manager_information['last_deadline_total_transfers']
    }
    manager_information_data = Information(**manager_information_data)
    manager_information_data.set_field_defaults()

    manager_leagues = manager_information['leagues']

    # Reconstruct the classic leagues assigning the manager and reset the id
    manager_classic_leagues = validate_json_against_model(manager_leagues['classic'], ClassicLeague)

    for league_data in manager_classic_leagues:
        # Extract nested active_phases and remove it from league_data_dict
        active_phases_data = league_data.active_phases
        league_data.league_id = league_data.id
        league_data.id = None
        league_data.manager = manager
        ClassicLeague.objects.filter(league_id=league_data.league_id, manager_id=manager.id).delete()
        league_data.save()

        for active_phase in active_phases_data:
            active_phase['classic_league'] = league_data
            active_phase['manager'] = manager
            active_phase.pop('league_id')
            active_phase['id'] = get_manager_league_phase(active_phase)
            ClassicLeaguePhase.objects.update_or_create(**active_phase)


    Information.save(manager_information_data)


def parse_and_save_manager_standings(managers_standings_data, event):
    """ Parse and save manager standing to Classic League

    Taking in the manager standings data from the API, assign it the league
    id, event and write to the database.
    :param managers_standings_data: manager standing data in JSON
    :param event: the event/gameweek being processed
    """
    standings_data = managers_standings_data['standings']

    league_id = managers_standings_data['league']['id']
    classic_league_standings = {ClassicLeagueStandings(**data_dict)
                                for data_dict in standings_data['results']}
    classic_league_standings = {obj.set_field_defaults() or obj for obj in classic_league_standings}

    custom_session = CustomSession(request)
    for standing in classic_league_standings:
        get_or_save_manager_team(league_id, standing.entry, event)
        standing.league_id = league_id
        standing.gameweek = event
        standing.id = get_manager_league_standing_id(standing)
        # Get the event total
        try:
            response = custom_session.custom_request('GET', properties.base_url +
                                    properties.event_standings_url.format(
                                        standing.entry))
            response.raise_for_status()
            event_data = formatted_json(response.text)
            event_current_data = event_data['current']
            this_event = next((item for item in event_current_data if item['event'] == event.id), None)
            standing.event_total = 0
            standing.total = 0
            if this_event is not None:
                standing.event_total = this_event.get('points')
                standing.total = this_event.get('total_points')
        except (RequestException, PermissionDenied) as exc:
            logger.info("Could not get event standings for %s: %s",
                        standing.entry, exc)
            continue
        standing.last_updated = datetime.now(timezone.utc)
        standing.save()


def parse_and_save_live_standings(live_standings_data):
    """ Parse and save live standing to Classic League Live

    Taking in the live league standings data from the API, write to the database.
    :param live_standings_data: manager standing data in JSON
    """
    elements = live_standings_data['elements']

    # Get a list of all players in Live data
    player_ids = [element['id'] for element in elements]

    # Retrieve all Player instances in one query
    players = Player.objects.filter(id__in=player_ids)

    # Create a dictionary for quick lookup
    player_dict = {player.id: player for player in players}

    for element in elements:
        id = element['id']
        stats_data = element['stats']

        player = player_dict.get(id)
        if player is None:
            # Skip if the player does not exist
            continue

        ClassicLeagueLiveStandings.objects.update_or_create(id=id, player = player, defaults={**stats_data})


def get_or_save_manager_team(league_id, manager_id, this_gameweek):
    """ If the manager doesn't exist in the database for this or previous
    gameweeks, get or update the details

    :param manager_id: league id,  managers id, this gameweek
    """

    try:
        # Only need to do this if the gameweek data has been checked and is finished, or it doesn't exist
        if not manager_needs_updating(league_id, manager_id, this_gameweek):
            return
    except ManagerTeam.DoesNotExist:
        logger.info("Manager Team %s doesn't exist or is out of date, "
                    "updating %s for gameweek %s", manager_id,
                    manager_id, this_gameweek)
    except Pick.DoesNotExist:
        logger.info("Picks for %s do not exist, updating....", manager_id)

    custom_session = CustomSession(request)
    try:
        response = custom_session.custom_request('GET', properties.base_url
                        + properties.manager_base_url.format(manager_id)
                        + properties.manager_picks_url.format(this_gameweek))
    except PermissionDenied:
        # Re-raise the exception
        raise

    logger.info("Updating manager %s for league %s for gameweek %s",
                manager_id, league_id, this_gameweek.id)
    manager_data = formatted_json(response.text)

    try:
        response = custom_session.custom_request('GET', properties.base_url
                        + properties.manager_base_url.format(manager_id))
    except PermissionDenied:
        # Re-raise the exception
        raise

    manager_information = formatted_json(response.text)
    manager = parse_and_save_manager(manager_id, this_gameweek, manager_data)

    parse_and_save_picks(manager, manager_data, this_gameweek)
    parse_and_save_history(manager, manager_data)
    parse_and_save_manager_information(manager, manager_information)


def get_league_standings(league_id, manager_id, event):
    """ Get the league standings for this page and the next (to enable the
    Next button """

    custom_session = CustomSession(request)

    if manager_needs_updating(league_id, manager_id, event):
        logger.info(
            "Updating league standings for manager %s "
            "for league %s for gameweek %s" % (manager_id, league_id, event.id)
        )

        try:
            response = custom_session.custom_request('GET',
                                    properties.base_url +
                                    properties.classic_league_url.format(
                                    league_id))
            response.raise_for_status()
        except (RequestException, PermissionDenied) as exc:
            logger.info("Could not get league for %s: %s",
                        league_id, exc)
            raise
        league_standings_data = formatted_json(response.text)
        parse_and_save_manager_standings(league_standings_data, event)


def get_live_league_standings(event):
    """ Get the live eague standings """

    custom_session = CustomSession(request)

    if live_data_needs_updating():

        try:
            response = custom_session.custom_request('GET',
                                                     properties.base_url +
                                                     properties.live_standings_url.format(
                                                         event.id))
            response.raise_for_status()
        except (RequestException, PermissionDenied) as exc:
            logger.info("Could not get live league for gameweek %s: %s",
                        event.id, exc)
            raise
        live_league_standings_data = formatted_json(response.text)
        parse_and_save_live_standings(live_league_standings_data)
        LastUpdated.objects.update_or_create(id=1,
                                             defaults={"live_data": datetime.now(timezone.utc)})
        logger.info("Finished retrieving live league data for gameweek %s ", event.id)
    else:
        logger.info("Don't need to update live league data for gameweek %s ", event.id)

def check_manager_exists(manager_id):
    """ Check if a manager exists using the API, and update if needs be """
    this_gameweek = get_current_gameweek()

    custom_session = CustomSession(request)
    try:
        response = custom_session.custom_request('GET',
                        properties.base_url +
                        properties.manager_base_url.format(manager_id) +
                        properties.manager_picks_url.format(this_gameweek))
    except (RequestException, PermissionDenied):
        raise ManagerNotFoundError(f'Manager {manager_id} not found')



def manager_needs_updating(league_id, manager_id, this_gameweek):
    """ Check if a manager needs to be updated for the inputted gameweek

    Only update if the gameweek is finished, data has been checked and we don't already have the data
    :param this_gameweek:
    :param manager_id:
    :return:
    """

    # If the gameweek is None, we're asking for the manager to be updated
    # regardless
    if this_gameweek is None:
        return True

    try:
        classic_league_standing = ClassicLeagueStandings.objects.get(entry=manager_id,
                                                                    league_id=league_id,
                                                                    gameweek=this_gameweek.id)
    except:
        # If no entry exists for this manager/league/gameweek, update it
        return True

    # Check that the gameweek data has been checked and finished, or that it is
    # the current gameweek
    if (this_gameweek.data_checked and this_gameweek.finished) or this_gameweek.is_current:
        if not (ClassicLeague.objects.filter(league_id=league_id, manager_id=manager_id)).exists():
            return True;

        # If the classic league standing has not been update in reload_manager_cache_time minutes, update it
        if not classic_league_standing.last_updated:
            return True

        threshold = datetime.now(timezone.utc) - timedelta(minutes=properties.reload_manager_cache_time)
        if threshold.timestamp() > classic_league_standing.last_updated.timestamp():
            return True

        # If the manager doesn't have 15 picks (potential timeout previously), update it
        if Pick.objects.filter(manager_id=manager_id,
                               gameweek=this_gameweek.id).count() != 15:
            return True

    return False


def live_data_needs_updating():
    return check_update_required(properties.reload_live_cache_time, DataTypeIdentifier.LIVE)


def manager_picks_notok():
    return Pick.objects.filter(
        ~Q(element__in=Subquery(Player.objects.values('id')))
    )


def get_manager_history_id(history):
    try:
        return History.objects.filter(manager_id = history.manager_id, event = history.event).first().id
    except:
        return None

def get_manager_pick_id(pick):
    try:
        return Pick.objects.filter(manager_id = pick.manager_id,
                                   gameweek = pick.gameweek,
                                   player_id = pick.player_id).first().id
    except:
        return None

def get_manager_league_standing_id(standing):
    try:
        return ClassicLeagueStandings.objects.filter(league_id = standing.league_id,
                                                     entry = standing.entry,
                                                     gameweek_id = standing.gameweek_id).first().id
    except:
        return None

def get_manager_league_phase(active_phase):
    try:
        return ClassicLeaguePhase.objects.filter(classic_league_id = active_phase.classic_league_id,
                                                 manager_id=active_phase.manager_id,
                                                 phase=active_phase.phase).first().id
    except:
        return None