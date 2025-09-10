import json
import os
import logging

from django.forms import model_to_dict

from fpl.definitions import ROOT_DIR
from fpl.properties.properties import get_properties
from teams.models import Team, TeamPreviousPosition
from utils.model_utils import validate_json_against_model

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

properties = get_properties()

def save_teams(data):
    """ Parse and save Team data

    :param data: downloaded raw data
    """
    logger.info('Got %s teams', str(len(data['teams'])))
    data = validate_json_against_model(data['teams'], Team)
    for team in data:
        team.save()


def load_and_save_team_previous_position():
    """ Load the team mapper data and save to db """
    file_to_import = os.path.join(ROOT_DIR, properties.team_previous_position_file)
    with open(file_to_import) as file:
        data = json.load(file)
    teams = [TeamPreviousPosition(**data_dict) for data_dict in data['teams']]
    for team in teams:

        team_data = model_to_dict(team, exclude=['id', 'season', 'this_team', 'team'])
        TeamPreviousPosition.objects.update_or_create(
            season=team.season,
            team=team.team,
            defaults={'this_team': Team.objects.get(id=team.team),
                      **team_data}
        )