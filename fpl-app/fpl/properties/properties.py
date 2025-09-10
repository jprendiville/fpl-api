""" This module is related to all things properties.

It loads, validates and puts the properties together for use throughout the
application.
"""

import configparser
import logging
import os
import sys
from datetime import datetime, timedelta

from django.utils import timezone
from str2bool import str2bool

from fpl.definitions import ROOT_DIR
from common.models.last_updated import LastUpdated
from fpl.enums.common_enums import DataTypeIdentifier

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class FPLProperties:
    """ Class to store FPL related properties """

    def __init__(self, base_url, bootstrap_static_url, fixtures_url,
                 player_url, manager_base_url, manager_picks_url,
                 classic_league_url, event_standings_url, live_standings_url,
                 event_status_url):
        """ Inits for FPL Properties """
        self.base_url = base_url
        self.bootstrap_static_url = bootstrap_static_url
        self.fixtures_url = fixtures_url
        self.player_url = player_url
        self.manager_base_url = manager_base_url
        self.manager_picks_url = manager_picks_url
        self.classic_league_url = classic_league_url
        self.event_standings_url = event_standings_url
        self.live_standings_url = live_standings_url
        self.event_status_url = event_status_url


class FDRProperties:
    """ Class to store FDR related properties """

    def __init__(self, fdr_easiest, fdr_hardest):
        """ Inits for FDR Properties """
        self.fdr_easiest = fdr_easiest
        self.fdr_hardest = fdr_hardest


class PathProperties:
    """ Class to store FDR related properties """

    def __init__(self, text_font, header_font, watermark, predictions_images, hashtags):
        """ Inits for FDR Properties """
        self.text_font = text_font
        self.header_font = header_font
        self.watermark = watermark
        self.predictions_images = predictions_images
        self.hashtags = hashtags


class GeneralProperties:
    """ Class to store general properties """

    def __init__(self, reload_full_cache_time, reload_live_cache_time,
                 reload_fixture_cache_time, reload_manager_cache_time,
                 retry_attempts, request_timeout, request_delay,
                 message_short_timeout, message_timeout, reload_data,
                 reload_fixtures, debug_mode, page_size, league_page_size,
                 progression_players_to_show, team_previous_position_file,
                 number_of_gameweeks, ml_enabled, minutes_played,
                 rolling_average, manager_ids, league_access_denied):
        """ Inits for General Properties """
        self.reload_full_cache_time = reload_full_cache_time
        self.reload_live_cache_time = reload_live_cache_time
        self.reload_fixture_cache_time = reload_fixture_cache_time
        self.reload_manager_cache_time = reload_manager_cache_time
        self.retry_attempts = retry_attempts
        self.request_timeout = request_timeout
        self.request_delay = request_delay
        self.message_short_timeout = message_short_timeout
        self.message_timeout = message_timeout
        self.reload_data = reload_data
        self.reload_fixtures = reload_fixtures
        self.debug_mode = debug_mode
        self.page_size = page_size
        self.league_page_size = league_page_size
        self.progression_players_to_show = progression_players_to_show
        self.team_previous_position_file = team_previous_position_file
        self.number_of_gameweeks = number_of_gameweeks
        self.ml_enabled = ml_enabled
        self.minutes_played = minutes_played
        self.rolling_average = rolling_average
        self.manager_ids = manager_ids
        self.league_access_denied = league_access_denied


class Properties:
    """ Class to store all properties """

    def __init__(self, fpl_properties, fdr_properties,
                 general_properties, path_properties):
        """ Inits for all properties """
        self.base_url = fpl_properties.base_url
        self.bootstrap_static_url = fpl_properties.bootstrap_static_url
        self.fixtures_url = fpl_properties.fixtures_url
        self.player_url = fpl_properties.player_url
        self.manager_base_url = fpl_properties.manager_base_url
        self.manager_picks_url = fpl_properties.manager_picks_url
        self.classic_league_url = fpl_properties.classic_league_url
        self.event_standings_url = fpl_properties.event_standings_url
        self.live_standings_url = fpl_properties.live_standings_url
        self.event_status_url = fpl_properties.event_status_url
        self.reload_full_cache_time = general_properties.reload_full_cache_time
        self.reload_live_cache_time = general_properties.reload_live_cache_time
        self.reload_fixture_cache_time = general_properties.reload_fixture_cache_time
        self.reload_manager_cache_time = general_properties.reload_manager_cache_time
        self.retry_attempts = \
            general_properties.retry_attempts
        self.request_timeout = general_properties.request_timeout
        self.request_delay = general_properties.request_delay
        self.message_short_timeout = general_properties.message_short_timeout
        self.message_timeout = general_properties.message_timeout
        self.reload_data = general_properties.reload_data
        self.reload_fixtures = general_properties.reload_fixtures
        self.debug_mode = general_properties.debug_mode
        self.page_size = general_properties.page_size
        self.league_page_size = general_properties.league_page_size
        self.progression_players_to_show = general_properties.progression_players_to_show
        self.team_previous_position_file = \
            general_properties.team_previous_position_file
        self.number_of_gameweeks = general_properties.number_of_gameweeks
        self.ml_enabled = general_properties.ml_enabled
        self.minutes_played = general_properties.minutes_played
        self.rolling_average = general_properties.rolling_average
        self.manager_ids = general_properties.manager_ids
        self.league_access_denied = general_properties.league_access_denied
        self.fdr_easiest = fdr_properties.fdr_easiest
        self.fdr_hardest = fdr_properties.fdr_hardest
        self.text_font = path_properties.text_font
        self.header_font = path_properties.header_font
        self.watermark = path_properties.watermark
        self.predictions_images = path_properties.predictions_images
        self.hashtags = path_properties.hashtags

    def any_property_blank(self):
        """
        Check if any property of the object is blank except for the
        'manager_ids' attribute.

        Returns: bool: True if any property is blank, False otherwise.
        """

        exception_attribute = 'manager_ids'
        for attr_name in dir(self):
            if not attr_name.startswith('__') and \
                getattr(self, attr_name) == "" and \
                attr_name != exception_attribute:
                return True
        return False


def check_update_required(cache_time, datatype):
    """
    Returns a boolean to say whether to reload data or not

    :param cache_time: integer number of minutes
    :param datatype: FPL or PREDICTION
    :return: True or False
    """
    update_required = False

    # Do we need to update?
    # Firstly check if we have previously recorded the last updated timestamps,
    # if not load the data
    lastupdated_obj = LastUpdated.objects.all().first()
    if not lastupdated_obj:
        # No record, so update
        update_required = True
    else:
        # Check if the last time is exceeded by the threshold, or we don't have
        # an entry
        if (datatype == DataTypeIdentifier.FPL and lastupdated_obj.fpl_data is None) or \
                (datatype == DataTypeIdentifier.LIVE and lastupdated_obj.live_data is None) or \
                (datatype == DataTypeIdentifier.FIXTURE and lastupdated_obj.fixture_data is None) or \
                (datatype == DataTypeIdentifier.PREDICTION and lastupdated_obj.prediction_data is None):
            return True
        if datatype == DataTypeIdentifier.FPL:
            last_updated = lastupdated_obj.fpl_data
        elif datatype == DataTypeIdentifier.LIVE:
            last_updated = lastupdated_obj.live_data
        elif datatype == DataTypeIdentifier.FIXTURE:
            last_updated = lastupdated_obj.fixture_data
        elif datatype == DataTypeIdentifier.PREDICTION:
            last_updated = lastupdated_obj.prediction_data
        else:
            last_updated = timezone.now()

        if last_updated is None:
            return True

        threshold = datetime.now() - timedelta(minutes=cache_time)
        if threshold.timestamp() > last_updated.timestamp():
            update_required = True

    return update_required


def check_player_history_required(reload_full_cache_time, player):
    """
    Check if the player history needs to be reloaded based on the reload
    threshold.

    Parameters:
    - reload_full_cache_time (int): The number of minutes after which the player
        history needs to be reloaded.
    - player (Player): The player object whose history is being checked.

    Returns:
    - bool: True if the player history needs to be reloaded, False otherwise.
    """

    if player.history_last_updated is None:
        return True

    threshold = datetime.now() - timedelta(minutes=reload_full_cache_time)
    if threshold.timestamp() > player.history_last_updated.timestamp():
        return True

    return False


def load_and_validate_props():
    """ Load and validate properties from the .ini """
    config = configparser.ConfigParser()
    config.read(os.path.join(ROOT_DIR, './properties.ini'))
    try:
        fpl_properties = FPLProperties(
            config['DEFAULT']['base_url'],
            config['DEFAULT']['bootstrap_static_url'],
            config['DEFAULT']['fixtures_url'],
            config['DEFAULT']['player_url'],
            config['DEFAULT']['manager_base_url'],
            config['DEFAULT']['manager_picks_url'],
            config['DEFAULT']['classic_league_url'],
            config['DEFAULT']['event_standings_url'],
            config['DEFAULT']['live_standings_url'],
            config['DEFAULT']['event_status_url'])
        general_properties = GeneralProperties(
            int(config['DEFAULT']['reload_full_cache_time']),
            int(config['DEFAULT']['reload_live_cache_time']),
            int(config['DEFAULT']['reload_fixture_cache_time']),
            int(config['DEFAULT']['reload_manager_cache_time']),
            int(config['DEFAULT']['retry_attempts']),
            int(config['DEFAULT']['request_timeout']),
            int(config['DEFAULT']['request_delay']),
            int(config['DEFAULT']['message_short_timeout']),
            int(config['DEFAULT']['message_timeout']),
            bool(str2bool(config['DEFAULT']['reload_data'])),
            bool(str2bool(config['DEFAULT']['reload_fixtures'])),
            bool(str2bool(config['DEFAULT']['debug_mode'])),
            int(config['DEFAULT']['page_size']),
            int(config['DEFAULT']['league_page_size']),
            int(config['DEFAULT']['progression_players_to_show']),
            config['DEFAULT']['team_previous_position_file'],
            int(config['DEFAULT']['number_of_gameweeks']),
            bool(str2bool(config['DEFAULT']['ml_enabled'])),
            int(config['DEFAULT']['minutes_played']),
            int(config['DEFAULT']['rolling_average']),
            config['DEFAULT']['manager_ids'],
            config['DEFAULT']['league_access_denied'])
        fdr_properties = FDRProperties(
            config['DEFAULT']['fdr_easiest'],
            config['DEFAULT']['fdr_hardest'])
        path_properties = PathProperties(
            config['DEFAULT']['text_font'],
            config['DEFAULT']['header_font'],
            config['DEFAULT']['watermark'],
            config['DEFAULT']['predictions_images'],
            config['DEFAULT']['hashtags'])

        properties = Properties(fpl_properties, fdr_properties,
                                general_properties, path_properties)
    except KeyError as key_exc:
        logger.critical("Cannot find key >%s< from properties.ini", key_exc)
        sys.exit(1)
    except ValueError as val_exc:
        logger.critical('Error with properties.ini config: %s for ', val_exc)
        sys.exit(1)

    # Validate the parameters
    if properties.any_property_blank():
        logger.critical("Invalid arguments")
        sys.exit(1)

    return properties


PROPERTIES = load_and_validate_props()


def get_properties():
    """ Function to return the properties """
    return PROPERTIES
