import json
import logging
from django.db import IntegrityError

from common.models.fixture import Fixture
from common.models.fixture_stats import FixtureStats
from fpl.enums.common_enums import FixtureStatIdentifier, HomeAwayIdentifier
from players.models import Player
from teams.models import Team
from utils.json_utils import formatted_json
from utils.model_utils import validate_json_against_model

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def save_fixtures(data, gameweek=None):
    """ Parse and save Fixture data

    :param data: downloaded raw data
    """
    logger.info('Got %s fixtures', len(data))
    data = validate_json_against_model(data, Fixture)
    for fixture in data:
        if not gameweek or (gameweek.id == fixture.event and not (fixture.finished or fixture.finished_provisional)):
            fixture.team_home = Team.objects.get(id=fixture.team_h)
            fixture.team_away = Team.objects.get(id=fixture.team_a)
            fixture.save()
            save_fixture_stats(fixture)

def save_fixture_stats(fixture):

    if not fixture.stats:
        return

    json_data = formatted_json(fixture.stats)

    for stat_data in json_data:
        # Get the identifier for the event (e.g., "goals_scored")
        identifier_str = stat_data.get('identifier')

        # Map the identifier string from JSON to the enum value
        try:
            identifier = FixtureStatIdentifier(identifier_str).value
        except ValueError:
            # If the identifier from the JSON is not valid, log an error and skip
            logger.error(f"Invalid identifier '{identifier_str}' in JSON for fixture {fixture.id}")
            continue

        # Iterate over both home ('h') and away ('a') stats generically
        for home_away_str, stats in [('home', stat_data.get('h', [])), ('away', stat_data.get('a', []))]:

            # Map the home_away string to the HomeAwayIdentifier enum
            home_away_enum = HomeAwayIdentifier.from_value(home_away_str)
            home_away_value = home_away_enum.default_value  # Get the canonical value ('home' or 'away')

            team = fixture.team_home if home_away_value == 'home' else fixture.team_away

            for stat in stats:
                try:
                    # Convert the player ID to a Player instance
                    try:
                        player = Player.objects.get(id=stat['element'])
                    except:
                        logger.error(f"Player does not exist.")

                    # Save or update the FixtureStat instance
                    fixturestat, created = FixtureStats.objects.update_or_create(
                        fixture=fixture,
                        identifier=identifier,
                        player=player,
                        team=team,
                        defaults={
                            'home_or_away': home_away_value,
                            'value': stat['value']
                        }
                    )
                except Player.DoesNotExist:
                    logger.error("Player with ID %s does not exist.", player.id)
                    continue
                except IntegrityError as e:
                    logger.error("Integrity error for Player with ID %s.", player.id)