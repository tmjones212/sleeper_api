from typing import Dict, List, Any
import requests
from models import League, Team, Roster
from exceptions import SleeperAPIException
import player_service

class LeagueService:
    def __init__(self, base_url: str, cache_service):
        self.base_url = base_url
        self.cache_service = cache_service
        self.scoring_settings = {}

    def get_league(self, league_id: str, fetch_all: bool = False) -> League:
        cache_key = f"league_{league_id}"
        if cache_key in self.cache_service.api_cache:
            league_data = self.cache_service.api_cache[cache_key]
        else:
            url = f"{self.base_url}/league/{league_id}"
            response = requests.get(url)
            response.raise_for_status()
            league_data = response.json()
            self.cache_service.api_cache[cache_key] = league_data
            self.cache_service.save_api_cache()
        
        league = League(**league_data)
        self.scoring_settings[league_id] = league.scoring_settings
        
        if fetch_all:
            league.teams = self.get_league_users(league_id)
            league_rosters = self.get_league_rosters(league_id)
            self._associate_rosters_with_teams(league.teams, league_rosters)
        
        return league

    def get_league_users(self, league_id: str) -> List[Team]:
        endpoint = f"{self.base_url}/league/{league_id}/users"
        response = self._make_request(endpoint)
        return [Team(**user) for user in response]

    def get_league_rosters(self, league_id: str) -> List[Roster]:
        endpoint = f"{self.base_url}/league/{league_id}/rosters"
        response = self._make_request(endpoint)
        return [Roster(**roster) for roster in response]

    def get_league_transactions(self, league_id: str, week: int) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/league/{league_id}/transactions/{week}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise SleeperAPIException(f"Error fetching league transactions: {str(e)}")

    def print_league_rosters(self, league_id: str, player_service):
        league = self.get_league(league_id, fetch_all=True)
        players = player_service.players

        print(f"Rosters for {league.name}:")
        for team in league.teams:
            print(f"\n{team.display_name} ({team.team_name}):")
            if team.roster:
                self._print_roster_section(team.roster, players, player_service)
            else:
                print("  No roster data available")
            print("---")

    def _print_roster_section(self, roster, players, player_service):
        print("  Starters:")
        for player_id in roster.starters:
            self._print_player(players, player_id, "    ", player_service)
        
        bench = set(roster.players) - set(roster.starters)
        if roster.reserve:
            bench -= set(roster.reserve)
        if roster.taxi:
            bench -= set(roster.taxi)
        
        if bench:
            print("  Bench:")
            for player_id in bench:
                self._print_player(players, player_id, "    ", player_service)
        
        if roster.reserve:
            print("  IR:")
            for player_id in roster.reserve:
                self._print_player(players, player_id, "    ", player_service)
        
        if roster.taxi:
            print("  Taxi Squad:")
            for player_id in roster.taxi:
                self._print_player(players, player_id, "    ", player_service)

    def _print_player(self, players, player_id: str, indent: str, player_service):
        player = players.get(player_id)
        if player:
            formatted_name = player_service.format_player_name(f"{player.first_name} {player.last_name}")
            print(f"{indent}- {formatted_name} ({player.position})")
        else:
            print(f"{indent}- Unknown Player (ID: {player_id})")

    def _associate_rosters_with_teams(self, teams: List[Team], rosters: List[Roster]):
        roster_dict = {roster.owner_id: roster for roster in rosters}
        for team in teams:
            team.roster = roster_dict.get(team.user_id)

    def _make_request(self, endpoint: str) -> Dict[str, Any]:
        cache_key = endpoint
        if cache_key in self.cache_service.api_cache:
            return self.cache_service.api_cache[cache_key]

        response = requests.get(endpoint)
        if response.status_code == 200:
            data = response.json()
            self.cache_service.api_cache[cache_key] = data
            self.cache_service.save_api_cache()
            return data
        else:
            raise SleeperAPIException(f"API request failed: {response.status_code} - {response.text}") 