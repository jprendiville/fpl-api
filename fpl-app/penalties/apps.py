""" This module is the application config for Penalties """

from django.apps import AppConfig


class PenaltiesConfig(AppConfig):
    """ Class model for Penalties """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'penalties'
