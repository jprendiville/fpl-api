import django_filters
from players.models import Player

class PlayerFilter(django_filters.FilterSet):
    # Exact matches
    player_team = django_filters.NumberFilter(field_name="player_team__id")
    player_type = django_filters.NumberFilter(field_name="player_type__id")
    status      = django_filters.CharFilter(field_name="status", lookup_expr="iexact")

    # Ranges / numeric filters
    min_cost    = django_filters.NumberFilter(field_name="now_cost", lookup_expr="gte")
    max_cost    = django_filters.NumberFilter(field_name="now_cost", lookup_expr="lte")
    min_points  = django_filters.NumberFilter(field_name="total_points", lookup_expr="gte")
    max_points  = django_filters.NumberFilter(field_name="total_points", lookup_expr="lte")

    class Meta:
        model = Player
        # These are simple exact-match fields that DRF/django-filters will expose automatically
        fields = [
            "player_team",     # /api/v1/players/?player_team=8
            "player_type",     # /api/v1/players/?player_type=3
            "status",          # /api/v1/players/?status=a
            # You can still pass min_/max_ params above even though they're not listed here
        ]
