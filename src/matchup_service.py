from typing import Dict, List, Optional
import requests
from models import Matchup
from player_service import PlayerService

class MatchupService:
    def __init__(self, base_url: str, cache_service):
        self.base_url = base_url
        self.cache_service = cache_service

    def get_matchups(
        self,
        league_id: str,
        week: int,
        current_week: Optional[int] = None,
        players: Optional[list] = None
    ) -> List[dict]:
        cache_key = f"{league_id}_{week}"
        current_week = current_week or week

        players_dict = PlayerService.players_list_to_dict(players) if players and isinstance(players, list) else players

        if cache_key in self.cache_service.matchups_cache:
            cached_matchups = self.cache_service.matchups_cache[cache_key]
            if not (week < current_week and any(matchup.points == 0 for matchup in cached_matchups)):
                if players:
                    for matchup in cached_matchups:
                        if isinstance(matchup, dict):
                            player_ids = matchup.get('players', [])
                        else:
                            player_ids = getattr(matchup, 'players', [])
                        player_names = [
                            players_dict.get(pid).name if players_dict.get(pid) else '' for pid in player_ids
                        ]
                        if isinstance(matchup, dict):
                            matchup['player_names'] = player_names
                        else:
                            setattr(matchup, 'player_names', player_names)
                return cached_matchups

        url = f"{self.base_url}/league/{league_id}/matchups/{week}"
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

            player_names = []
            if players:
                player_names = [
                    players_dict.get(pid).name if players_dict.get(pid) else '' for pid in matchup_data.get('players', [])
                ]

            matchup = Matchup(
                matchup_id=matchup_data.get('matchup_id'),
                roster_id=matchup_data.get('roster_id'),
                points=matchup_data.get('points'),
                players=matchup_data.get('players', []),
                starters=matchup_data.get('starters', []),
                players_points=players_points,
                starters_points=starters_points,
                custom_points=None
            )
            if player_names:
                setattr(matchup, 'player_names', player_names)
            matchups.append(matchup)

        self.cache_service.matchups_cache[cache_key] = matchups
        self.cache_service.save_matchups_cache()
        return matchups

    def get_all_matchups(self, league_id: str, current_week: int) -> Dict[int, List[Matchup]]:
        return {
            week: self.get_matchups(league_id, week, current_week)
            for week in range(1, current_week + 1)
        }
    
    def get_matchups_by_year(self, league_id: str, year: int, max_week: int = 18) -> Dict[int, List[Matchup]]:
        """Get all matchups for a specific year"""
        return {
            week: self.get_matchups(league_id, week, max_week)
            for week in range(1, max_week + 1)
        }
    
    def calculate_head_to_head_records(self, all_matchups_data: Dict[str, Dict[int, List[Matchup]]], team_names: List[str]) -> Dict[str, Dict[str, Dict[str, int]]]:
        """Calculate head-to-head records between all teams across all seasons"""
        records = {}
        
        # Initialize records structure
        for team in team_names:
            records[team] = {}
            for opponent in team_names:
                if team != opponent:
                    records[team][opponent] = {'wins': 0, 'losses': 0, 'ties': 0}
        
        # Process all matchups across all years
        for year, year_matchups in all_matchups_data.items():
            for week, matchups in year_matchups.items():
                # Group matchups by matchup_id to find head-to-head games
                matchup_groups = {}
                for matchup in matchups:
                    if matchup.matchup_id not in matchup_groups:
                        matchup_groups[matchup.matchup_id] = []
                    matchup_groups[matchup.matchup_id].append(matchup)
                
                # Process each matchup group (should be 2 teams)
                for matchup_id, teams in matchup_groups.items():
                    if len(teams) == 2:
                        team1, team2 = teams
                        team1_name = self._get_team_name_by_roster_id(team1.roster_id, team_names)
                        team2_name = self._get_team_name_by_roster_id(team2.roster_id, team_names)
                        
                        if team1_name and team2_name and team1_name in records and team2_name in records:
                            if team1.points > team2.points:
                                records[team1_name][team2_name]['wins'] += 1
                                records[team2_name][team1_name]['losses'] += 1
                            elif team2.points > team1.points:
                                records[team2_name][team1_name]['wins'] += 1
                                records[team1_name][team2_name]['losses'] += 1
                            else:
                                records[team1_name][team2_name]['ties'] += 1
                                records[team2_name][team1_name]['ties'] += 1
        
        return records
    
    def _get_team_name_by_roster_id(self, roster_id: int, team_names: List[str]) -> str:
        """Helper method to get team name by roster ID - you may need to implement this based on your data structure"""
        # This is a placeholder - you'll need to implement the actual mapping
        # based on how you're storing the roster_id to team_name mapping
        return None
    
    def format_matchups_for_display(self, matchups: List[Matchup], roster_to_team_mapping: Dict[int, str]) -> List[Dict]:
        """Format matchups for display in the template"""
        # Group matchups by matchup_id
        matchup_groups = {}
        for matchup in matchups:
            if matchup.matchup_id not in matchup_groups:
                matchup_groups[matchup.matchup_id] = []
            matchup_groups[matchup.matchup_id].append(matchup)
        
        formatted_matchups = []
        for matchup_id, teams in matchup_groups.items():
            if len(teams) == 2:
                team1, team2 = teams
                
                # Determine winner/loser/tie
                if team1.points > team2.points:
                    team1_class, team2_class = 'winner', 'loser'
                elif team2.points > team1.points:
                    team1_class, team2_class = 'loser', 'winner'
                else:
                    team1_class, team2_class = 'tie', 'tie'
                
                formatted_matchup = {
                    'matchup_id': matchup_id,
                    'teams': [
                        {
                            'name': roster_to_team_mapping.get(team1.roster_id, f"Team {team1.roster_id}"),
                            'score': team1.points,
                            'result_class': team1_class
                        },
                        {
                            'name': roster_to_team_mapping.get(team2.roster_id, f"Team {team2.roster_id}"),
                            'score': team2.points,
                            'result_class': team2_class
                        }
                    ]
                }
                formatted_matchups.append(formatted_matchup)
        
        return formatted_matchups 