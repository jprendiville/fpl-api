from enum import Enum

from django.db import models


class FixtureStatIdentifier(Enum):
    GOALS_SCORED = "goals_scored"
    ASSISTS = "assists"
    OWN_GOALS = "own_goals"
    PENALTIES_SAVED = "penalties_saved"
    PENALTIES_MISSED = "penalties_missed"
    YELLOW_CARDS = "yellow_cards"
    RED_CARDS = "red_cards"
    SAVES = "saves"
    BONUS = "bonus"
    BPS = "bps"
    DEFENSIVE_CONTRIBUTION = "defensive_contribution"
    MANAGER_UNDERDOG_WIN = "mng_underdog_win"
    MANAGER_UNDERDOG_DRAW = "mng_underdog_draw"

    @classmethod
    def choices(cls):
        return [(key.value, key.name.replace('_', ' ').title()) for key in cls]

    @classmethod
    def from_value(cls, value):
        for item in cls:
            if item.value == value:
                return item
        raise ValueError(f"'{value}' is not a valid value for {cls.__name__}")


class HomeAwayIdentifier(Enum):
    HOME = ("home", "Home", "HOME")
    AWAY = ("away", "Away", "AWAY")

    @classmethod
    def choices(cls):
        """
        Returns a list of tuples compatible with Django's 'choices' parameter.
        """
        return [(member.value[0], member.value[0].capitalize()) for member in cls]

    @classmethod
    def from_value(cls, value):
        """
        Returns the enum member matching any of the provided variations.
        """
        for member in cls:
            if value in member.value:
                return member
        raise ValueError(f"'{value}' is not a valid {cls.__name__}")

    @property
    def default_value(self):
        """
        Returns the canonical value (the first one in the tuple) for the enum member.
        """
        return self.value[0]


class DataTypeIdentifier(Enum):
    """ Enum for game results data types """
    FPL = 'fpl'
    LIVE = 'live'
    FIXTURE = 'fixture'
    PREDICTION = 'prediction'

    @classmethod
    def choices(cls):
        return [(choice.value, choice.name.title()) for choice in cls]


class ChipIdentifier(models.TextChoices):
    BENCH_BOOST = "bboost", "Bench Boost"
    FREE_HIT = "freehit", "Free Hit"
    WILDCARD = "wildcard", "Wildcard"
    TRIPLE_CAPTAIN = "3xc", "Triple Captain"