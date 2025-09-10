""" This is the scheduler to reload data periodically """
import logging
from datetime import datetime, timedelta
import pytz

from apscheduler.schedulers.background import BackgroundScheduler

from fpl.properties.properties import load_and_validate_props
from .load_data import load

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def start():
    """ Reload data based on settings in the properties """
    properties = load_and_validate_props()

    scheduler = BackgroundScheduler(timezone=pytz.utc)
    # Adding a job to the sceduler. It will run every reload_full_cache_time minutes
    # and the first run will be in reload_full_cache_time minutes, so not straight
    # away
    scheduler.add_job(load, 'interval',
                      minutes=properties.reload_full_cache_time,
                      next_run_time=datetime.now() + timedelta(
                          minutes=properties.reload_full_cache_time))
    logger.info("Reloading data in %s minutes",
                properties.reload_full_cache_time)
    scheduler.start()
