""" This module is used to build up a managers team and show upcoming
opponents for each player """

from django.db.models import Q
from django.utils import timezone
from multipledispatch import dispatch

from common.models.event_status import EventStatus
from players.models import Fixture


class LeagueStandings:
    """ Class to store league standings """

    picks = []

    @dispatch(object, object)
    def __init__(self, standing, picks):
        """ Inits for league standings """
        self.standing = standing
        self.picks = picks

    def __str__(self):
        """ Return a formatted representation of league standing """
        return f"{self.standing.rank}: {self.standing.player_name} " \
               f"- {self.standing.entry_name}"

    def set_opponents(self, picks):
        """ Set the opponents for the managers picks

        :param picks: The managers picks
        :return: Updated list of picks with the opponents
        """
        updated_picks = []
        for pick in picks:
            gameweek_opponents = Fixture.objects.filter(Q(event=pick.gameweek),
                                        Q(team_away=pick.player.player_team) |
                                        Q(team_home=pick.player.player_team))
            opponents_to_add = []
            for this_opponent in gameweek_opponents:
                # If this players team is the home team, the opponent is the
                # away team. And vice versa
                updated_opponent = this_opponent.team_away \
                    if this_opponent.team_home == pick.player.player_team \
                    else this_opponent.team_home
                updated_opponent = updated_opponent.short_name + ' (H) ' \
                    if this_opponent.team_home == pick.player.player_team \
                    else updated_opponent.short_name + ' (A)'
                opponents_to_add.append(updated_opponent)
            pick.opponents = opponents_to_add
            updated_picks.append(pick)
        return updated_picks

    def bonus_added(event):
        # Find the latest live status
        latest = EventStatus.objects.filter(points__isnull=False, gameweek=event).exclude(points="").order_by('-date').first()

        return True if (latest and latest.bonus_added) else False;