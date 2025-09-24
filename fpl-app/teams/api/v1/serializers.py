from rest_framework import serializers

from common.utils import get_current_gameweek, get_next_n_games_fdr
from fpl.properties.properties import get_properties
from teams.models import Team

properties = get_properties()

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ("id", "name", "short_name", "code")
        read_only_fields = fields

class TeamFdrSerializer(serializers.ModelSerializer):
    next_games = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ["id", "name", "short_name", "code", "next_games"]

    def get_next_games(self, team):
        next_gw = get_current_gameweek()
        return get_next_n_games_fdr(team, next_gw, properties.number_of_gameweeks)