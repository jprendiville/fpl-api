""" This module is a class to store manager details temporarily """

from multipledispatch import dispatch


class Manager:
    """ Class to store manager details """

    @dispatch(object, object, object, object, object, object)
    def __init__(self, manager_team, information, picks, classic_leagues,
                 this_league, total_expected):
        """ Inits for a Manager using team, information, picks, classic
        leagues, this league and expected points """
        self.manager_team = manager_team
        self.information = information
        self.picks = picks
        self.classic_leagues = classic_leagues
        self.this_league = this_league
        self.total_expected = total_expected

    @dispatch(object, object, object, object, object)
    def __init__(self, manager_team, information, picks, classic_leagues,
                 total_expected):
        """ Inits for a Manager using team, information, picks, classic
        leagues and expected points """
        self.manager_team = manager_team
        self.information = information
        self.picks = picks
        self.classic_leagues = classic_leagues
        self.total_expected = total_expected

    @dispatch(object, object, object)
    def __init__(self, manager_team, information, classic_leagues):
        """ Inits for an Manager using team, information and classic
        leagues """
        self.manager_team = manager_team
        self.information = information
        self.classic_leagues = classic_leagues

    def __str__(self):
        """ Return a formatted representation of a manager """
        return f"{self.information.name} ({self.information.id})"
