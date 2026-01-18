import logging

from django.forms import model_to_dict

from common.models.event import Event
from common.models.event_chip_play import EventChipPlay
from common.models.event_overrides import EventOverride
from common.models.event_status import EventStatus
from common.utils import get_gameweek
from utils.model_utils import validate_json_against_model

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def save_events(data):
    """ Parse and save Events data

    :param data: downloaded raw data
    """
    logger.info('Got %s events', str(len(data['events'])))
    event_instances = []
    event_overrides = []
    event_chipplays = []
    for event_data in data['events']:
        # Preserve overrides
        overrides = event_data.pop('overrides', None)
        chip_plays = event_data.pop('chip_plays', None)

        # Validate and create the Event instance
        validated_events = validate_json_against_model([event_data], Event)
        if validated_events:
            event = validated_events[0]
            event_instances.append(event)

            # Pair the event with its overrides
            if overrides:
                event_overrides.append((event, overrides))

            if chip_plays:
                event_chipplays.append((event, chip_plays))

    for event in event_instances:
        event.save()

    for event, overrides in event_overrides:
            # Validate and create the EventOverride instance
        validated_overrides = validate_json_against_model([overrides], EventOverride)
        if validated_overrides:
            override = validated_overrides[0]
            override.gameweek_id = event.id
            override.save()

    for event, chip_plays in event_chipplays:
        for chip_data in chip_plays:
            chip_data["event"] = event
            validated_chip = validate_json_against_model([chip_data], EventChipPlay)
            if validated_chip:
                chip = validated_chip[0]
                chip.event_id = event.id
                chip.save()


def save_event_status(data):
    """ Parse and save Event Status data

    :param data: downloaded raw data
    """
    logger.info('Got %s event status', str(len(data['status'])))
    data = validate_json_against_model(data['status'], EventStatus)
    for event_status in data:
        event_status_data = model_to_dict(event_status, exclude=['id', 'event', 'date', 'gameweek'])
        EventStatus.objects.update_or_create(
            event=event_status.event,
            date=event_status.date,
            defaults={'gameweek': get_gameweek(event_status.event),
                      **event_status_data}
        )

def save_event_overrides(data):
    """ Parse and save Event Override data

    :param data: downloaded raw data
    """
    pass