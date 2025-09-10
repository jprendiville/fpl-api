""" This module is the application config for Players """

import logging
import sys

from django.apps import AppConfig

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class PlayersConfig(AppConfig):
    """ Class model for Players """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'players'

    def ready(self):
        """ Updating the data """
        if 'runserver' in sys.argv:
            from fpl.dataloader import scheduled_updater
            scheduled_updater.start()
