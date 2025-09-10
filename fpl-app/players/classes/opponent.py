""" This module is a class to work with Opponents for a player or team """


class Opponent:
    """ Class to store the opponent for a team/player """

    def __init__(self, event):
        """ Inits for an Opponent Event """
        self.event = event
        self.color = 0
        self.fdr = 0
        self.fdrwithdraw = 0
        self.teams = []

    def __str__(self):
        """ Return a formatted representation of opponents """
        return f"{self.event} - {self.teams}"

    def clear_teams(self):
        """ Clear the opponents for a team """
        self.teams = []

    def add_team(self, team):
        """ Add to a team to list of opponents """
        self.teams.append(team)

    def show_opponents(self):
        """ Show the opponents for a team """
        opponent = ""
        size = len(self.teams) - 1
        for index, team in enumerate(self.teams):
            opponent += team
            # We only want a '/' if it is not the last element
            if index < size:
                opponent += ' / '
        return opponent
