# app/api/serializers.py
from rest_framework import serializers

from players.api.v1.serializers import PlayerListSerializer


class ManagerRequestSerializer(serializers.Serializer):
    """
    Accept either:
      - {"manager_ids": [123, 456]}
      - {"manager_ids": "123,456"}
    """
    manager_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
        required=False,
    )
    # also accept CSV in the same field
    def to_internal_value(self, data):
        raw = data.get("manager_ids")
        if isinstance(raw, str):
            try:
                ids = [int(x) for x in raw.split(",") if x.strip()]
            except ValueError:
                raise serializers.ValidationError({"manager_ids": "Must be a list of integers or CSV string of ints."})
            data = {"manager_ids": ids}
        return super().to_internal_value(data)

class ManagerInfoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    formatted_name = serializers.CharField(required=False, allow_blank=True)

class ManagerTeamSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    display_active_chip = serializers.CharField(required=False, allow_blank=True)

class ClassicLeagueSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    rank = serializers.IntegerField(required=False, allow_null=True)

# Your Pick object likely has: position, is_sub, player, format_expected_points, etc.
class PickSerializer(serializers.Serializer):
    position = serializers.IntegerField()
    is_sub = serializers.BooleanField()
    # You had "player_name" in the template; but frontend can use player.web_name.
    # Keep it if you still want it:
    player_name = serializers.CharField(required=False, allow_blank=True)

    # Reuse the same Player serializer so "next_games" looks identical to Players page
    player = PlayerListSerializer(read_only=True)

    # expose expected points the way your template used it
    format_expected_points = serializers.CharField(required=False, allow_blank=True)

class ManagerSerializer(serializers.Serializer):
    # This is NOT a ModelSerializer; Manager is a plain class
    information = ManagerInfoSerializer()
    manager_team = ManagerTeamSerializer()
    total_expected = serializers.DecimalField(max_digits=8, decimal_places=2, required=False)
    classic_leagues = ClassicLeagueSerializer(many=True, required=False)
    # this_league appears in one constructor; make it optional:
    this_league = ClassicLeagueSerializer(required=False, allow_null=True)
    picks = PickSerializer(many=True)
