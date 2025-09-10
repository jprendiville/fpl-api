""" Utilities to rebuild things """
import logging
import datetime

from django.db.models import Q, Subquery
from django.utils import timezone

from fpl.dataloader.load.load_predictions import get_predictions
from fpl.enums.common_enums import DataTypeIdentifier
from fpl.properties.properties import check_update_required, get_properties
from players.models import Event, LastUpdated

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

properties = get_properties()


def rebuild_predictions(force_refresh=False, recalculate_all=False):
    # For each gameweek > 1, get predictions
    if force_refresh or check_update_required(properties.reload_full_cache_time, DataTypeIdentifier.PREDICTION):

        logger.info("Starting rebuild at %s", datetime.datetime.now())
        if recalculate_all:
            gameweeks = Event.objects.filter(Q(id__gt=1) & Q(id__lte=Subquery
                        (Event.objects.filter(Q(is_next=True) | Q(is_current=True)).values('id')[:1]))).order_by('id')
        else:
            gameweeks = Event.objects.filter(id=Subquery(Event.objects.filter(Q(is_next=True) | Q(is_current=True)).values('id')[:1]))
        for gameweek in gameweeks:
            get_predictions(gameweek)
        LastUpdated.objects.update_or_create(id=1, defaults={"prediction_data": timezone.now()})
        logger.info("Finished rebuild at %s", datetime.datetime.now())
    else:
        logger.info('Dont need to rebuild predictions')


# if __name__ == '__main__':
#     rebuild_predictions(True, True)

        if __name__ == '__main__':
            rebuild_predictions(True, True)
