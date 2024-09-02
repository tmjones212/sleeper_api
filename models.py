from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import re

@dataclass
class LeagueMetadata:
    auto_continue: str
    division_1: str
    division_1_avatar: str
    division_2: str
    division_2_avatar: str
    keeper_deadline: str
    latest_league_winner_roster_id: str

@dataclass
class LeagueSettings:
    best_ball: int
    waiver_budget: int
    disable_adds: int
    divisions: int
    capacity_override: int
    waiver_bid_min: int
    taxi_deadline: int
    draft_rounds: int
    reserve_allow_na: int
    start_week: int
    playoff_seed_type: int
    playoff_teams: int
    veto_votes_needed: int
    num_teams: int
    daily_waivers_hour: int
    playoff_type: int
    taxi_slots: int
    sub_start_time_eligibility: int
    daily_waivers_days: int
    playoff_week_start: int
    waiver_clear_days: int
    reserve_allow_doubtful: int
    commissioner_direct_invite: int
    veto_auto_poll: int
    reserve_allow_dnr: int
    taxi_allow_vets: int
    waiver_day_of_week: int
    playoff_round_type: int
    reserve_allow_out: int
    reserve_allow_sus: int
    veto_show_votes: int
    trade_deadline: int
    taxi_years: int
    daily_waivers: int
    disable_trades: int
    pick_trading: int
    type: int
    max_keepers: int
    waiver_type: int
    max_subs: int
    league_average_match: int
    trade_review_days: int
    bench_lock: int
    offseason_adds: int
    leg: int
    daily_waivers_base: int
    reserve_slots: int
    reserve_allow_cov: int
    daily_waivers_last_ran: int

@dataclass
class League:
    name: str
    status: str
    metadata: LeagueMetadata
    settings: LeagueSettings
    avatar: str
    company_id: Optional[str]
    last_message_id: str
    scoring_settings: Dict[str, float]
    season: str
    season_type: str
    shard: int
    sport: str
    draft_id: str
    last_author_avatar: Optional[str]
    last_author_display_name: str
    last_author_id: str
    last_author_is_bot: bool
    last_message_attachment: Optional[str]
    last_message_text_map: Optional[Dict[str, Any]]
    last_message_time: int
    last_pinned_message_id: Optional[str]
    last_read_id: Optional[str]
    league_id: str
    previous_league_id: str
    roster_positions: List[str]
    group_id: Optional[str]
    bracket_id: Optional[str]
    loser_bracket_id: Optional[str]
    total_rosters: int
    teams: List['Team'] = field(default_factory=list)

    def __post_init__(self):
        # Convert metadata dict to LeagueMetadata object if it's not already
        if isinstance(self.metadata, dict):
            self.metadata = LeagueMetadata(**self.metadata)
        if isinstance(self.settings, dict):
            self.settings = LeagueSettings(**self.settings)

    def __str__(self):
        return f"{self.name} (ID: {self.league_id})"

    def __repr__(self):
        return f"League(league_id='{self.league_id}', name='{self.name}', total_rosters={self.total_rosters})"


@dataclass
class Team:
    user_id: str
    display_name: str
    metadata: Dict[str, Any]
    roster: Optional['Roster'] = None

    @property
    def team_name(self):
        return self.metadata.get('team_name')

    def __str__(self):
        return f"{self.display_name} ({self.team_name or 'No team name'})"

    def __repr__(self):
        return f"Team(user_id='{self.user_id}', display_name='{self.display_name}', team_name='{self.team_name}')"


class Player:
    def __init__(self, **kwargs):
        self.player_id = kwargs.get('player_id')
        self.first_name = kwargs.get('first_name')
        self.last_name = kwargs.get('last_name')
        self.full_name = kwargs.get('full_name')
        self.position = kwargs.get('position')
        self.team = kwargs.get('team')
        self.age = kwargs.get('age')
        self.status = kwargs.get('status')
        self.height = kwargs.get('height')
        self.weight = kwargs.get('weight')
        self.years_exp = kwargs.get('years_exp')
        self.college = kwargs.get('college')
        self.fantasy_positions = kwargs.get('fantasy_positions')
        self.active = kwargs.get('active')
        self.number = kwargs.get('number')
        self.birth_date = kwargs.get('birth_date')
        self.injury_status = kwargs.get('injury_status')
        
        # Create a formatted name property
        self.name = self.format_name(f"{self.first_name} {self.last_name}")

    def format_name(self, s):
        # If there is a (, dump everything from there on
        s = s.split('(')[0]

        # Initial replacements and formatting
        s = s.strip().upper()
        s = re.sub(r'[,+.*]', '', s)
        s = re.sub(r'\s+(JR|SR|III|II|IV|V)$', '', s)
        s = s.replace("'", "").replace("-", " ")

        # Additional specific replacements
        replacements = {
            "MITCHELL T": "MITCH T",
            "ROBBY ANDERSON": "ROBBIE ANDERSON",
            "WILLIAM ": "WILL ",
            "OLABISI": "BISI",
            "ELI MITCHELL": "ELIJAH MITCHELL",
            "CADILLAC WILLIAMS": "CARNELL WILLIAMS",
            "GABE DAVIS": "GABRIEL DAVIS",
            "JEFFERY ": "JEFF ",
            "JOSHUA ": "JOSH ",
            "CHAUNCEY GARDNER": "CJ GARDNER",
            "BENNETT SKOWRONEK": "BEN SKOWRONEK",
            "NATHANIEL DELL": "TANK DELL",
        }

        for old, new in replacements.items():
            s = s.replace(old, new)

        # Handle specific starting names
        if s.startswith("MICHAEL "):
            s = s.replace("MICHAEL ", "MIKE ", 1)
        if s.startswith("KENNETH "):
            s = s.replace("KENNETH ", "KEN ", 1)

        return s

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Player(player_id={self.player_id}, name='{self.name}')"


class Team:
    def __init__(self, **kwargs):
        self.user_id = kwargs.get('user_id')
        self.league_id = kwargs.get('league_id')
        self.display_name = kwargs.get('display_name')
        self.avatar = kwargs.get('avatar')
        self.is_bot = kwargs.get('is_bot')
        self.is_owner = kwargs.get('is_owner')
        self.metadata = kwargs.get('metadata', {})
        self.settings = kwargs.get('settings')

        # Extract specific metadata fields
        self.team_name = self.metadata.get('team_name')
        self.avatar_url = self.metadata.get('avatar')
        self.allow_pn = self.metadata.get('allow_pn')
        self.allow_sms = self.metadata.get('allow_sms')
        self.archived = self.metadata.get('archived')
        self.show_mascots = self.metadata.get('show_mascots')

        # Store all attributes, even those not explicitly defined
        for key, value in kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)

    def __str__(self):
        return f"{self.display_name} ({self.team_name or 'No team name'})"

    def __repr__(self):
        return f"Team(user_id={self.user_id}, display_name='{self.display_name}', team_name='{self.team_name}')"


@dataclass
class Matchup:
    roster_id: int
    points: float
    matchup_id: int
    players: List[str]
    starters: List[str]
    starters_points: List[float]

from typing import List, Dict, Optional

class Roster:
    def __init__(self, **kwargs):
        self.roster_id = kwargs.get('roster_id')
        self.owner_id = kwargs.get('owner_id')
        self.league_id = kwargs.get('league_id')
        self.players: List[str] = kwargs.get('players', [])
        self.starters: List[str] = kwargs.get('starters', [])
        self.reserve: Optional[List[str]] = kwargs.get('reserve')
        self.taxi: Optional[List[str]] = kwargs.get('taxi')
        self.metadata: Dict[str, str] = kwargs.get('metadata', {})
        self.settings: Dict[str, int] = kwargs.get('settings', {})
        
        # Extract specific settings
        self.wins = self.settings.get('wins', 0)
        self.losses = self.settings.get('losses', 0)
        self.ties = self.settings.get('ties', 0)
        self.fpts = self.settings.get('fpts', 0)
        self.waiver_position = self.settings.get('waiver_position', 0)
        self.waiver_budget_used = self.settings.get('waiver_budget_used', 0)

    def __str__(self):
        return f"Roster ID: {self.roster_id}, Owner ID: {self.owner_id}"

    def __repr__(self):
        return f"Roster(roster_id={self.roster_id}, owner_id='{self.owner_id}', players_count={len(self.players)})"
