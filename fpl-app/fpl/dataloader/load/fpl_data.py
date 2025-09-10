""" Check if we need to reload fpl data. If we do, download it, parse it and
save to the database """
import json
import logging

from django.core.exceptions import PermissionDenied
from django.utils import timezone
from requests import ConnectTimeout, HTTPError, request

from common.models.last_updated import LastUpdated
from fpl.dataloader.load.load_element_types import save_element_types
from fpl.dataloader.load.load_events import save_event_overrides, \
    save_event_status, save_events
from fpl.dataloader.load.load_fixtures import save_fixtures
from fpl.dataloader.load.load_phases import save_phases
from fpl.dataloader.load.load_players import save_players
from fpl.dataloader.load.load_teams import save_teams
from fpl.enums.common_enums import DataTypeIdentifier

from fpl.exceptions.fpl_data_exceptions import FplDataError, \
    FplPlayerDataError
from fpl.properties.properties import check_update_required, get_properties
from utils.custom_requests import CustomSession
from utils.json_utils import formatted_json

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

properties = get_properties()


def load_and_save_fpl_data(force_refresh, result_queue):
    """ Check if we need to reload data, if we do download it can save each
    element """
    custom_session = CustomSession(request)
    try:
        if force_refresh or check_update_required(properties.reload_full_cache_time, DataTypeIdentifier.FPL):

            try:
                response_static = custom_session.custom_request(
                    'GET', properties.base_url +
                    properties.bootstrap_static_url,
                    timeout=properties.request_timeout)
                response_static.raise_for_status()
                json_static_str = formatted_json(response_static.text)

                response_fixtures = custom_session.custom_request('GET',
                                            properties.base_url +
                                            properties.fixtures_url,
                                            timeout=properties.request_timeout)
                response_fixtures.raise_for_status()
                json_fixtures_str = formatted_json(response_fixtures.text)

                response_event_status = custom_session.custom_request('GET',
                                                                  properties.base_url +
                                                                  properties.event_status_url,
                                                                  timeout=properties.request_timeout)
                response_event_status.raise_for_status()
                json_event_status_str = formatted_json(response_event_status.text)

                save_teams(json_static_str)
                save_element_types(json_static_str)
                save_events(json_static_str)
                save_event_status(json_event_status_str)
                save_event_overrides(json_event_status_str)
                save_phases(json_static_str)
                save_players(json_static_str, result_queue)
                save_fixtures(json_fixtures_str)

                LastUpdated.objects.update_or_create(id=1,
                                defaults={"fpl_data": timezone.now()})
                logger.info("Done saving fpl data")
            except FplPlayerDataError as exc:
                logger.error("Failed to retrieve fpl player data: %s", exc)
                raise FplPlayerDataError
            except FplDataError as exc:
                logger.error("Failed to retrieve fpl data: %s", exc)
                raise FplDataError
        else:
            logger.info("Don't need to update fpl data")
    except (ConnectTimeout, HTTPError, PermissionDenied) as exc:
        logger.error("Failed to retrieve fpl data: %s", exc)
        raise FplDataError


def load_and_save_player_data(force_refresh, result_queue):
    """ Check if we need to reload data, if we do download it can save each
    element """
    custom_session = CustomSession(request)
    try:
        if force_refresh or check_update_required(properties.reload_full_cache_time, DataTypeIdentifier.FPL):

            try:
                response_static = custom_session.custom_request(
                    'GET', properties.base_url +
                           properties.bootstrap_static_url,
                    timeout=properties.request_timeout)
                response_static.raise_for_status()
                json_static_str = formatted_json(response_static.text)

                save_players(json_static_str, result_queue)

                LastUpdated.objects.update_or_create(id=1,
                                                     defaults={"fpl_data": timezone.now()})
                logger.info("Done saving player data")
            except FplPlayerDataError as exc:
                logger.error("Failed to retrieve player player data: %s", exc)
                raise FplPlayerDataError
            except FplDataError as exc:
                logger.error("Failed to retrieve player data: %s", exc)
                raise FplDataError
        else:
            logger.info("Don't need to update player data")
    except (ConnectTimeout, HTTPError, PermissionDenied) as exc:
        logger.error("Failed to retrieve player data: %s", exc)
        raise FplDataError


def load_and_save_fixture_data(gameweek):
    """ Check if we need to reload data, if we do download it can save each
    element """
    if properties.reload_fixtures and check_update_required(properties.reload_fixture_cache_time, DataTypeIdentifier.FIXTURE):
        custom_session = CustomSession(request)
        try:
            response_fixtures = custom_session.custom_request('GET',
                                                              properties.base_url +
                                                              properties.fixtures_url,
                                                              timeout=properties.request_timeout)
            response_fixtures.raise_for_status()
            json_fixtures_str = formatted_json(response_fixtures.text)

            save_fixtures(json_fixtures_str, gameweek)
            LastUpdated.objects.update_or_create(id=1,
                                                 defaults={"fixture_data": timezone.now()})
            logger.info("Done saving fixture data")
        except (ConnectTimeout, HTTPError, PermissionDenied) as exc:
            logger.error("Failed to retrieve fixture data: %s", exc)
            raise FplDataError
