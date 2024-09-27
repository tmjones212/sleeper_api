import json
import os
import re
from typing import Any, Dict, List, Optional
import requests
from customer_json_encoder import CustomJSONEncoder
from exceptions import SleeperAPIException
from models import League, PlayerInfo, ProjectedStats, SleeperProjections, Team, Matchup, Player, Roster, PlayerProjection, PlayerStats, Transaction
import csv
from datetime import datetime, timedelta

class SleeperAPI:
    BASE_URL = "https://api.sleeper.app/v1"

    def __init__(self):
        self.players = self.load_players_from_file()
        self.cache = {}
        self.load_cache()
        self.scoring_settings = {}
        self.stats_cache = self.load_stats_cache()
        self.projections_cache = self.load_projections_cache()
        self.matchups_cache = self.load_matchups_cache()

    def get_team_name(self, league_id: str, roster_id: int) -> str:
        league = self.get_league(league_id, fetch_all=True)
        for team in league.teams:
            if team.roster and team.roster.roster_id == roster_id:
                return team.display_name
        return f"Unknown Team (Roster ID: {roster_id})"

    def get_player_name(self, player_id: str) -> str:
        player = self.players.get(player_id)
        if player:
            return f"{player.first_name} {player.last_name}"
        else:
            return f"Unknown Player (ID: {player_id})"

    
    def get_league_transactions(self, league_id: str, week: int) -> List[Transaction]:
        url = f"{self.BASE_URL}/league/{league_id}/transactions/{week}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            transactions = []
            for transaction_data in data:
                transaction = Transaction.from_dict(transaction_data)
                transactions.append(transaction)
            
            return transactions
        except requests.RequestException as e:
            raise SleeperAPIException(f"Error fetching Sleeper transactions: {str(e)}")

    def get_league_trades(self, league_id: str, week: int) -> List[Transaction]:
        transactions = self.get_league_transactions(league_id, week)
        return [t for t in transactions if t.type == "trade"]

    def fetch_players_from_api(self) -> Dict[str, Player]:
        url = f"{self.BASE_URL}/players/nfl"
        print('getting players from api...')
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        players = {player_id: Player(**player_data) for player_id, player_data in data.items()}
        self.save_players_to_file(players)  # Save the fetched players to file
        return players

    def save_players_to_file(self, players: Dict[str, Player], filename="players.json"):
        with open(filename, 'w') as f:
            json.dump({pid: {k: v for k, v in vars(p).items() if not k.startswith('_')} for pid, p in players.items()}, f)
        print(f"Players data saved to {filename}")

    def load_players_from_file(self, filename="players.json") -> Dict[str, Player]:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                print('loading players from file...')
                data = json.load(f)
            return {pid: Player(**player_data) for pid, player_data in data.items()}
        else:
            print(f"File {filename} not found. Fetching data from API...")
            return self.fetch_players_from_api()

    def get_player_position(self, player_id: str) -> str:
        player = self.players.get(player_id)
        if player:
            return player.position
        else:
            return "UNKNOWN"

    def get_player_name(self, player_id: str) -> str:
        player = self.players.get(player_id)
        if player:
            return player.name
        else:
            return f"Unknown Player ({player_id})"

    def get_league(self, league_id: str, fetch_all: bool = False) -> League:
        cache_key = f"league_{league_id}"
        if cache_key in self.cache:
            league_data = self.cache[cache_key]
        else:
            url = f"{self.BASE_URL}/league/{league_id}"
            response = requests.get(url)
            response.raise_for_status()
            league_data = response.json()
            self.cache[cache_key] = league_data
            self.save_cache()
        
        league = League(**league_data)
        self.scoring_settings[league_id] = league.scoring_settings
        
        if fetch_all:
            league.teams = self.get_league_users(league_id)
            league_rosters = self.get_league_rosters(league_id)
            self._associate_rosters_with_teams(league.teams, league_rosters)
        
        return league

    def get_projections(self, year: int, week: int, position: str) -> List[PlayerProjection]:
        cache_key = f"{year}_{week}_{position}"
        if cache_key in self.projections_cache:
            return self.projections_cache[cache_key]

        projections = SleeperProjections.get_projections(year, week, position)
        self.projections_cache[cache_key] = projections
        self.save_projections_cache()
        return projections
    
    def get_league_users(self, league_id: str) -> List[Team]:
        endpoint = f"{self.BASE_URL}/league/{league_id}/users"
        response = self._make_request(endpoint)
        return [Team(**user) for user in response]

    def get_league_rosters(self, league_id: str) -> List[Roster]:
        endpoint = f"{self.BASE_URL}/league/{league_id}/rosters"
        response = self._make_request(endpoint)
        return [Roster(**roster) for roster in response]

    def _associate_rosters_with_teams(self, teams: List[Team], rosters: List[Roster]):
        roster_dict = {roster.owner_id: roster for roster in rosters}
        for team in teams:
            team.roster = roster_dict.get(team.user_id)

    def get_matchups(self, league_id: str, week: int, current_week: Optional[int] = None) -> List[Matchup]:
        cache_key = f"{league_id}_{week}"
    
        # If current_week is not provided, use the week parameter
        current_week = current_week or week

        # Check if the matchup is in the cache
        if cache_key in self.matchups_cache:
            cached_matchups = self.matchups_cache[cache_key]
            
            # If it's a past week (relative to current_week) and any matchup has zero points, fetch new data
            if week < current_week and any(matchup.points == 0 for matchup in cached_matchups):
                print(f"Cached matchups for week {week} have zero points. Fetching new data.")
            else:
                return cached_matchups

        url = f"{self.BASE_URL}/league/{league_id}/matchups/{week}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        matchups = []
        for matchup_data in data:
            players_points = {}
            starters_points = []
            for player_id, points in matchup_data.get('players_points', {}).items():
                players_points[player_id] = points
                if player_id in matchup_data.get('starters', []):
                    starters_points.append(points)

            matchup = Matchup(
                matchup_id=matchup_data.get('matchup_id'),
                roster_id=matchup_data.get('roster_id'),
                points=matchup_data.get('points'),
                players=matchup_data.get('players', []),
                starters=matchup_data.get('starters', []),
                players_points=players_points,
                starters_points=starters_points
            )
            matchups.append(matchup)

        self.matchups_cache[cache_key] = matchups
        self.save_matchups_cache()
        return matchups

    def get_all_matchups(self, league_id: str, current_week: int) -> Dict[int, List[Matchup]]:
        all_matchups = {}
        for week in range(1, current_week + 1):
            all_matchups[week] = self.get_matchups(league_id, week, current_week)
        return all_matchups
    
    def get_traded_picks(self, league_id: str) -> List[Dict[str, Any]]:
        url = f"{self.BASE_URL}/league/{league_id}/traded_picks"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise SleeperAPIException(f"Error fetching traded picks: {str(e)}")

    def get_all_traded_picks(self, league_id: str) -> List[Dict[str, Any]]:
        all_traded_picks = []
        current_league_id = league_id

        while current_league_id:
            traded_picks = self.get_traded_picks(current_league_id)
            all_traded_picks.extend(traded_picks)

            league = self.get_league(current_league_id)
            current_league_id = league.previous_league_id

        return all_traded_picks

    def get_player_fields(self):
        url = f"{self.BASE_URL}/players/nfl"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Get the first player in the dictionary
        first_player = next(iter(data.values()))
        
        # Pretty print the fields
        print(json.dumps(first_player, indent=2))

    def print_team_fields(self, league_id: str):
        endpoint = f"{self.BASE_URL}/league/{league_id}/users"
        response = self._make_request(endpoint)
        if response and len(response) > 0:
            print(json.dumps(response[0], indent=2))
        else:
            print("No users found in the league or empty response.")
    
    
    def _make_request(self, endpoint: str) -> Dict[str, Any]:
        cache_key = endpoint
        if cache_key in self.cache:
            return self.cache[cache_key]

        response = requests.get(endpoint)
        if response.status_code == 200:
            data = response.json()
            self.cache[cache_key] = data
            self.save_cache()
            return data
        else:
            raise SleeperAPIException(f"API request failed: {response.status_code} - {response.text}")

    def print_league_rosters(self, league_id: str):
        league = self.get_league(league_id, fetch_all=True)
        players = self.get_players()

        print(f"Rosters for {league.name}:")
        for team in league.teams:
            print(f"\n{team.display_name} ({team.team_name}):")
            if team.roster:
                print("  Starters:")
                for player_id in team.roster.starters:
                    self._print_player(players, player_id, "    ")
                
                bench = set(team.roster.players) - set(team.roster.starters)
                if team.roster.reserve:
                    bench -= set(team.roster.reserve)
                if team.roster.taxi:
                    bench -= set(team.roster.taxi)
                
                if bench:
                    print("  Bench:")
                    for player_id in bench:
                        self._print_player(players, player_id, "    ")
                
                if team.roster.reserve:
                    print("  IR:")
                    for player_id in team.roster.reserve:
                        self._print_player(players, player_id, "    ")
                
                if team.roster.taxi:
                    print("  Taxi Squad:")
                    for player_id in team.roster.taxi:
                        self._print_player(players, player_id, "    ")
            else:
                print("  No roster data available")
            print("---")

    def _print_player(self, players: Dict[str, Player], player_id: str, indent: str):
        player = players.get(player_id)
        if player:
            formatted_name = self.format_player_name(f"{player.first_name} {player.last_name}")
            print(f"{indent}- {formatted_name} ({player.position})")
        else:
            print(f"{indent}- Unknown Player (ID: {player_id})")

    @staticmethod
    def format_player_name(name: str) -> str:
        name = name.split('(')[0]  # Remove anything in parentheses
        name = name.strip().upper()
        name = re.sub(r'[,+.*]', '', name)
        name = re.sub(r'\s+(JR|SR|III|II|IV|V)$', '', name)
        name = name.replace("'", "").replace("-", " ")

        # Additional specific replacements
        replacements = {
            "MITCHELL": "MITCH",
            "WILLIAM": "WILL",
            "BENJAMIN": "BEN",
            "MICHAEL": "MIKE",
            "JOSHUA": "JOSH",
            "ROBERT": "ROB",
            "CHRISTOPHER": "CHRIS",
            "KENNETH": "KEN",
            "JEFFREY": "JEFF",
            "GABRIEL": "GABE",
            "NATHANIEL": "NATE",
        }

        for old, new in replacements.items():
            name = name.replace(f"{old} ", f"{new} ")

        return name

    def get_current_week(self) -> int:
        current_date = datetime.now().date()
        week_ranges = self._get_week_ranges()

        for week, (start_date, end_date) in sorted(week_ranges.items()):
            if current_date <= end_date:
                return week

        # If we're past the last week, return the last week number
        return max(week_ranges.keys())
    
    def get_current_season_year(self) -> int:
        week_ranges = self._get_week_ranges()
        current_date = datetime.now().date()
        
        for week, (start_date, end_date) in week_ranges.items():
            if current_date <= end_date:
                return start_date.year
        
        # If we're past the last game, return the year of the last game
        return max(end_date.year for _, end_date in week_ranges.values())

    def _get_week_ranges(self):
        week_ranges = {}
        with open('2024 Game Dates.csv', 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                week = int(row['WeekNum'])
                date = datetime.strptime(row['ScheduleDate'], '%Y-%m-%d %H:%M:%S').date()
                
                if week not in week_ranges:
                    week_ranges[week] = [date, date]  # [start_date, end_date]
                else:
                    week_ranges[week][0] = min(week_ranges[week][0], date)
                    week_ranges[week][1] = max(week_ranges[week][1], date)

        # Adjust the start and end dates for each week
        sorted_weeks = sorted(week_ranges.keys())
        for i in range(len(sorted_weeks)):
            current_week = sorted_weeks[i]
            
            # Set end date (no change needed, it's already the last game day of the week)
            
            # Set start date (except for week 1)
            if i > 0:
                previous_week = sorted_weeks[i-1]
                week_ranges[current_week][0] = week_ranges[previous_week][1] + timedelta(days=1)

        return week_ranges

    def load_cache(self, filename="api_cache.json"):
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                self.cache = json.load(f)

    def save_cache(self, filename="api_cache.json"):
        with open(filename, 'w') as f:
            json.dump(self.cache, f, default=lambda o: vars(o) if hasattr(o, '__dict__') else str(o))

    def clear_cache(self):
        self.cache = {}
        self.stats_cache = {}
        self.projections_cache = {}
        self.matchups_cache = {}
        self.save_cache()
        self.save_stats_cache()
        self.save_projections_cache()
        self.save_matchups_cache()

    def get_stats(self, year: int, week: int, position: str, league_id: str) -> Dict[str, PlayerStats]:
        cache_key = f"{year}_{week}_{position}_{league_id}"
        if cache_key in self.stats_cache:
            print(f"Debug: Using cached stats for {cache_key}")
            return self.stats_cache[cache_key]

        print(f"Debug: Fetching stats for {cache_key}")
        url = f"{self.BASE_URL}/stats/nfl/{year}/{week}?season_type=regular&position[]={position}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        stats = {}
        scoring_settings = self.scoring_settings.get(league_id, {})

        for player_id, item in data.items():
            player_stats = item.get('stats', {})
            fantasy_points = self._calculate_fantasy_points(player_stats, scoring_settings)
            stats[player_id] = PlayerStats(
                player_id=player_id,
                fantasy_points=fantasy_points,
                **player_stats
            )
            print(f"Debug: Player {player_id} - Fantasy Points: {fantasy_points}")

        self.stats_cache[cache_key] = stats
        self.save_stats_cache()
        return stats

    def _calculate_fantasy_points(self, player_stats: Dict[str, float], scoring_settings: Dict[str, float]) -> float:
        fantasy_points = 0
        for stat, value in player_stats.items():
            if stat in scoring_settings:
                fantasy_points += value * scoring_settings[stat]
        return fantasy_points

    def load_stats_cache(self, filename="stats_cache.json"):
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
                return {k: {player_id: PlayerStats(**stats) for player_id, stats in v.items()} for k, v in data.items()}
        return {}

    def save_stats_cache(self, filename="stats_cache.json"):
        with open(filename, 'w') as f:
            json.dump(self.stats_cache, f, cls=CustomJSONEncoder)

    def load_projections_cache(self, filename="projections_cache.json"):
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
                return {k: [self._reconstruct_player_projection(p) for p in v] for k, v in data.items()}
        return {}

    def save_projections_cache(self, filename="projections_cache.json"):
        with open(filename, 'w') as f:
            json.dump(self.projections_cache, f, cls=CustomJSONEncoder)

    def load_matchups_cache(self, filename="matchups_cache.json"):
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                serialized_cache = json.load(f)
                return {key: [Matchup(**matchup_data) for matchup_data in matchups]
                        for key, matchups in serialized_cache.items()}
        return {}

    def save_matchups_cache(self, filename="matchups_cache.json"):
        serializable_cache = {}
        for key, matchups in self.matchups_cache.items():
            serializable_cache[key] = [matchup.__dict__ for matchup in matchups]
        
        with open(filename, 'w') as f:
            json.dump(serializable_cache, f)

    def _reconstruct_player_projection(self, data):
        return PlayerProjection(
            player=PlayerInfo(**data['player']),
            stats=ProjectedStats(**data['stats']),
            week=data['week'],
            year=data['year'],
            opponent=data['opponent']
        )
