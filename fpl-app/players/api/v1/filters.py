import django_filters
from django_filters import OrderingFilter

from players.models import Player, PlayerPrediction


class PlayerFilter(django_filters.FilterSet):
    # Exact matches
    player_team = django_filters.NumberFilter(field_name="player_team__id")
    player_type = django_filters.NumberFilter(field_name="player_type__id")
    status      = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    max_cost    = django_filters.NumberFilter(field_name="now_cost", lookup_expr="lte")

    class Meta:
        model = Player
        # These are simple exact-match fields that DRF/django-filters will expose automatically
        fields = [
            "player_team",     # /api/v1/players/?player_team=8
            "player_type",     # /api/v1/players/?player_type=3
            "status",          # /api/v1/players/?status=a
            "max_cost",        # /api/v1/players/?max_cost=9.3
            # You can still pass min_/max_ params above even though they're not listed here
        ]

class PredictionFilter(django_filters.FilterSet):
    # Exact matches
    player_team = django_filters.NumberFilter(field_name="player_team__id")
    player_type = django_filters.NumberFilter(field_name="player_type__id")
    status      = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    max_cost    = django_filters.NumberFilter(field_name="now_cost", lookup_expr="lte")

    class Meta:
        model = PlayerPrediction
        # These are simple exact-match fields that DRF/django-filters will expose automatically
        fields = [
            "player_team",     # /api/v1/players/?player_team=8
            "player_type",     # /api/v1/players/?player_type=3
            "status",          # /api/v1/players/?status=a
            "max_cost",        # /api/v1/players/?max_cost=9.3
            # You can still pass min_/max_ params above even though they're not listed here
        ]

class OrderingFilterCompat(OrderingFilter):
    def get_schema_operation_parameters(self, view):
        getter = getattr(super(), "get_schema_operation_parameters", None)
        if callable(getter):
            return getter(view)
        ordering_param = getattr(view, "ordering_param", "ordering")
        fields = getattr(view, "ordering_fields", None)
        desc = "Ordering parameter. Use '-' prefix for descending."
        if fields:
            desc += f" Allowed values: {', '.join(fields)}."
        return [{
            "name": ordering_param,
            "required": False,
            "in": "query",
            "description": desc,
            "schema": {"type": "string"},
        }]