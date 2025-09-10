""" This module is a class to deal with Manager exceptions. """

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class FplDataError(Exception):
    """ Currently does nothing, but is a placeholder for the future """
    pass

class FplPlayerDataError(Exception):
    """ Currently does nothing, but is a placeholder for the future """
    pass

class PlayerHistoryError(Exception):
    """ Currently does nothing, but is a placeholder for the future """
    pass
