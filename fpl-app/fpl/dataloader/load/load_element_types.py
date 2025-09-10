import logging

from players.models import ElementType
from utils.model_utils import validate_json_against_model

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def save_element_types(data):
    """ Parse and save Player Element Type data

    :param data: downloaded raw data
    """
    logger.info('Got %s player types', str(len(data['element_types'])))
    data = validate_json_against_model(data['element_types'], ElementType)
    for element_type in data:
        element_type.save()