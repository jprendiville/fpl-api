""" This module is a class to deal with Manager exceptions. """

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ManagerNotFoundError(Exception):
    """ Currently does nothing, but is a placeholder for the future """
    pass

class PickNotFoundError(Exception):
    """ Currently does nothing, but is a placeholder for the future """
    pass