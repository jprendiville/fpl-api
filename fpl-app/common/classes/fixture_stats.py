class FixtureStats:
    def __init__(self, player, fixture=None, team=None, home_or_away=None, **kwargs):
        self.player = player
        self.fixture = fixture
        self.team = team
        self.home_or_away = home_or_away.default_value

        # Store stats as a dictionary
        self.stats = {
            'goals_scored': kwargs.get('goals_scored', 0),
            'assists': kwargs.get('assists', 0),
            'own_goals': kwargs.get('own_goals', 0),
            'penalties_saved': kwargs.get('penalties_saved', 0),
            'penalties_missed': kwargs.get('penalties_missed', 0),
            'yellow_cards': kwargs.get('yellow_cards', 0),
            'red_cards': kwargs.get('red_cards', 0),
            'saves': kwargs.get('saves', 0),
            'bonus': kwargs.get('bonus', 0),
            'bps': kwargs.get('bps', 0)
        }

    def as_dict(self):
        return {
            'player': self.player,
            'fixture': self.fixture,
            'team': self.team,
            'home_or_away': self.home_or_away,
            **self.stats
        }
