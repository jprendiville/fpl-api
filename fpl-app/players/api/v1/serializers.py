# players/api/v1/serializers.py
from rest_framework import serializers

from common.utils import get_next_gameweek, get_next_n_games_fdr
from fpl.properties.properties import get_properties
from players.models import Player, ElementType, PlayerPrediction
from players.models.player_history import PlayerHistory
from settings.api.v1.serializers import PlayerStatusSerializer
from teams.api.v1.serializers import TeamSerializer
from rest_framework import serializers

properties = get_properties()

class ElementTypeMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElementType
        fields = (
            "id",
            "singular_name_short",  # e.g., GKP/DEF/MID/FWD
            "plural_name_short",    # e.g., GKs/DEFs/MIDs/FWDs
            "singular_name",        # e.g., Goalkeeper
            "plural_name",          # e.g., Goalkeepers
        )
        read_only_fields = fields


class PlayerListSerializer(serializers.ModelSerializer):
    team = TeamSerializer(source="player_team", read_only=True)
    type = ElementTypeMiniSerializer(source="player_type", read_only=True)
    status = PlayerStatusSerializer(source='player_status', read_only=True)
    next_games = serializers.SerializerMethodField()

    class Meta:
        model = Player
        exclude = ("player_team", "player_type")

    def get_next_games(self, obj):
        next_gameweek = get_next_gameweek()
        return get_next_n_games_fdr(
            obj.player_team,
            next_gameweek,
            properties.number_of_gameweeks,
        )


class PlayerDefenceSerializer(serializers.ModelSerializer):
    # replace raw FKs with nested
    team = TeamSerializer(source="player_team", read_only=True)
    type = ElementTypeMiniSerializer(source="player_type", read_only=True)
    status = PlayerStatusSerializer(source='player_status', read_only=True)
    next_games = serializers.SerializerMethodField()

    class Meta:
        model = Player
        # include all model fields except the FK sources (we expose them as team/type above)
        exclude = ("player_team", "player_type")

    def get_next_games(self, obj):
        next_gameweek = get_next_gameweek()
        return get_next_n_games_fdr(
            obj.player_team,
            next_gameweek,
            properties.number_of_gameweeks,
        )

class ElementTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElementType
        fields = "__all__"

class PlayerHistorySerializer(serializers.ModelSerializer):
    opponent_short_name = serializers.CharField(source="opponent.short_name", read_only=True)
    opponent_name = serializers.CharField(source="opponent.name", read_only=True)
    home_away = serializers.SerializerMethodField()

    class Meta:
        model = PlayerHistory
        fields = '__all__'

    def get_home_away(self, obj: "PlayerHistory") -> str:
        return 'H' if obj.was_home else 'A'

class PlayerPredictionSerializer(serializers.ModelSerializer):
    player = PlayerListSerializer(read_only=True)

    class Meta:
        model = PlayerPrediction
        fields = [
            "id",
            "player",
            "prediction",
            "gameweek_id",
        ]

class PlayerPredictionHistorySerializer(serializers.ModelSerializer):
    opponent_short_name = serializers.CharField(source="opponent.short_name", read_only=True)
    opponent_name = serializers.CharField(source="opponent.name", read_only=True)
    home_away = serializers.SerializerMethodField()
    web_name = serializers.CharField(source="player.web_name", read_only=True)
    team = TeamSerializer(source="player.player_team", read_only=True)
    position = serializers.CharField(source="player.player_type.singular_name_short", read_only=True)
    status = PlayerStatusSerializer(source='player_status', read_only=True)

    class Meta:
        model = PlayerPrediction
        fields = [
            "id",
            "opponent_short_name",
            "opponent_name",
            "home_away",
            "web_name",
            "team",
            "position",
            "element",
            "total_points",
            "prediction",
            "team_h_score",
            "team_a_score",
            "was_home",
            "finished",
            "last_updated",
            "season",
            "gameweek",
        ]

    def get_home_away(self, obj):
        return "H" if obj.was_home else "A"