import json
import os
import re
from typing import Any, Dict, List, Optional
import requests
from exceptions import SleeperAPIException
from models import League, SleeperProjections, Team, Matchup, Player, Roster, PlayerProjection

class SleeperAPI:
    BASE_URL = "https://api.sleeper.app/v1"

    def __init__(self):
        self.players = self.load_players_from_file()

    def fetch_players_from_api(self) -> Dict[str, Player]:
        url = f"{self.BASE_URL}/players/nfl"
        print('getting players from api...')
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return {player_id: Player(**player_data) for player_id, player_data in data.items()}

    def save_players_to_file(self, filename="players.json"):
        players = self.fetch_players_from_api()
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
        url = f"{self.BASE_URL}/league/{league_id}"
        response = requests.get(url)
        response.raise_for_status()
        league_data = response.json()
        
        league = League(**league_data)
        
        if fetch_all:
            league.teams = self.get_league_users(league_id)
            league_rosters = self.get_league_rosters(league_id)
            self._associate_rosters_with_teams(league.teams, league_rosters)
        
        return league

    def get_projections(self,year: int, week: int, position: str) -> List[PlayerProjection]:
        url = f"{self.BASE_URL}/projections/nfl/{year}/{week}?season_type=regular&position={position}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return SleeperProjections.get_projections(year, week, position)
    
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

    def get_matchups(self, league_id: str, week: int) -> List[Matchup]:
        url = f"{self.BASE_URL}/league/{league_id}/matchups/{week}"
        response = requests.get(url)
        response.raise_for_status()
        matchup_data = response.json()
        
        return [Matchup(
            roster_id=m['roster_id'],
            points=m['points'],
            matchup_id=m['matchup_id'],
            players=m['players'],
            starters=m['starters'],
            starters_points=m['starters_points'],
            players_points={player: m['players_points'].get(player, 0) for player in m['players']}
        ) for m in matchup_data]

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
        response = requests.get(endpoint)
        if response.status_code == 200:
            return response.json()
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

