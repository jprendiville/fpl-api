import logging

from common.models.phase import Phase
from utils.model_utils import validate_json_against_model

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def save_phases(data):
    """ Parse and save Phase data

    :param data: downloaded raw data
    """
    logger.info('Got %s phases', str(len(data['phases'])))
    data = validate_json_against_model(data['phases'], Phase)
    for phase in data:
        phase.save()