from rest_framework import serializers
from teams.models import Team

class TeamMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ("id", "name", "short_name", "code")
        read_only_fields = fields