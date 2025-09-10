""" Load configs and download/save data """
from datetime import timedelta
from queue import Queue
import logging

from common.models.last_updated import LastUpdated
from fpl.dataloader.load.fpl_data import load_and_save_fpl_data
from fpl.dataloader.load.load_teams import load_and_save_team_previous_position
from fpl.exceptions.fpl_data_exceptions import FplDataError, FplPlayerDataError
from fpl.properties.properties import get_properties
from utils.rebuild_predictions import rebuild_predictions

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

properties = get_properties()


def load():
    """ Load the configs and make the call to update/save data """
    logger.info('Loading data')
    result_queue = Queue()
    if properties.reload_data:
        try:
            load_and_save_fpl_data(False, result_queue)
            load_and_save_team_previous_position()
            if properties.ml_enabled:
                rebuild_predictions(False, False)
            last_updated = LastUpdated.objects.filter().first()
            next_update = last_updated.fpl_data + timedelta(minutes=properties.reload_full_cache_time)
            logger.info(f'Done loading data. Reloading again in '
                        f'{properties.reload_full_cache_time} minutes on '
                        f'{next_update.strftime("%d-%m-%Y")} at '
                        f'{next_update.strftime("%H:%M:%S")}')
        except FplDataError:
            logger.info('Failed to retrieve FPL data')
        except FplPlayerDataError:
            logger.info('Failed to retrieve FPL player data')
    else:
        logger.info('Properties say not to reload data')
