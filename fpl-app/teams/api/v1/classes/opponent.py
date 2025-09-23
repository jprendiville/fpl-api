""" This module is a class to work with Opponents for a player or team """

from dataclasses import dataclass, field, asdict
from typing import List


@dataclass
class Opponent:
    """Store the opponent(s) for a team/player in a given event/gameweek."""

    event: int
    color: int = 0
    fdr: int = 0
    fdrwithdraw: int = 0
    teams: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        return f"{self.event} - {self.teams}"

    def clear_teams(self) -> None:
        self.teams.clear()

    def add_team(self, team: str) -> None:
        self.teams.append(team)

    @property
    def text(self) -> str:
        """Friendly display, e.g. 'AVL / WOL'"""
        return " / ".join(self.teams)

    def to_dict(self) -> dict:
        """Return a dict that is JSON serializable."""
        d = asdict(self)
        d["text"] = self.text
        return d
