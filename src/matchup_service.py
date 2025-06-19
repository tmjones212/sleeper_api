from typing import Dict, List, Optional, Any
import requests
import json
import os
from datetime import datetime
from models import Matchup
from player_service import PlayerService

class MatchupService:
    def __init__(self, base_url_or_client, cache_service=None):
        # Support both old pattern (base_url, cache_service) and new pattern (client)
        if isinstance(base_url_or_client, str):
            self.base_url = base_url_or_client
            self.cache_service = cache_service
            self.client = None
        else:
            # Assume it's a client object
            self.client = base_url_or_client
            self.base_url = base_url_or_client.BASE_URL if hasattr(base_url_or_client, 'BASE_URL') else None
            self.cache_service = base_url_or_client.cache_service if hasattr(base_url_or_client, 'cache_service') else None
        
        self._matchup_breakdowns = None
        
        # Define league IDs for each year
        self.league_years = {
            2025: "1181025001438806016",
            2024: "1048308938824937472", 
            2023: "916445745966915584",
            2022: "839251409999347712"
        }

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
    
    def load_matchup_breakdowns(self) -> Dict[str, Any]:
        """Load preprocessed matchup breakdown data with player names and positions"""
        if self._matchup_breakdowns is not None:
            return self._matchup_breakdowns
        
        breakdowns_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'matchup_breakdowns.json')
        try:
            with open(breakdowns_file, 'r') as f:
                data = json.load(f)
                self._matchup_breakdowns = data.get('matchups', {})
                return self._matchup_breakdowns
        except FileNotFoundError:
            print(f"Matchup breakdowns file not found: {breakdowns_file}")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error parsing matchup breakdowns JSON: {e}")
            return {}
    
    def get_matchup_player_breakdown(self, league_id: str, week: int, roster_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed player breakdown for a specific matchup"""
        breakdowns = self.load_matchup_breakdowns()
        cache_key = f"{league_id}_{week}"
        
        if cache_key not in breakdowns:
            return None
        
        week_matchups = breakdowns[cache_key]
        for matchup in week_matchups:
            if matchup.get('roster_id') == roster_id:
                return matchup
        
        return None
    
    def get_all_player_breakdowns_for_matchup(self, league_id: str, week: int, matchup_id: int) -> List[Dict[str, Any]]:
        """Get player breakdowns for all teams in a specific matchup"""
        breakdowns = self.load_matchup_breakdowns()
        cache_key = f"{league_id}_{week}"
        
        if cache_key not in breakdowns:
            return []
        
        week_matchups = breakdowns[cache_key]
        matchup_teams = []
        
        for matchup in week_matchups:
            if matchup.get('matchup_id') == matchup_id:
                matchup_teams.append(matchup)
        
        return matchup_teams 
    
    def get_matchup_data(self, league_id: str, year: int = None, week: int = None) -> Dict[str, Any]:
        """Get all matchup data for the specified parameters."""
        if not self.client:
            raise ValueError("Client instance required for get_matchup_data method")
            
        # Get league info for league name (use most recent league)
        current_league_id = self.league_years.get(2025, league_id)
        league = self.client.league_service.get_league(current_league_id)
        
        # Get all years data
        all_years_data = self._get_all_years_matchup_data()
        
        # Get team names from the most recent year for consistency
        roster_to_team_mapping = self._get_roster_to_team_mapping(current_league_id)
        team_names = list(set(roster_to_team_mapping.values()))
        
        # Calculate head-to-head records across all available years
        head_to_head_records = self._calculate_cross_year_head_to_head_records(all_years_data, team_names)
        
        # If specific year is requested, filter to that year
        if year is not None:
            filtered_years_data = {year: all_years_data.get(year, {})}
            selected_year = year
        else:
            filtered_years_data = all_years_data
            selected_year = 'all'
        
        # Create matchups by week for the template
        matchups_by_week = {}
        if year and year in all_years_data:
            matchups_by_week = all_years_data[year]
        
        # Get current week matchups if specified and year is specified
        current_week_matchups = []
        if week and year and year in all_years_data and week in all_years_data[year]:
            current_week_matchups = all_years_data[year][week]
        
        return {
            'league_id': league_id,
            'league_name': league.name,
            'selected_year': selected_year,
            'selected_week': week or 'all',
            'max_week': 18,
            'available_years': sorted(self.league_years.keys(), reverse=True),
            'all_years_data': filtered_years_data,
            'matchups_by_week': matchups_by_week,
            'current_week_matchups': current_week_matchups,
            'team_names': sorted(team_names),
            'head_to_head_records': head_to_head_records,
            'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _get_roster_to_team_mapping(self, league_id: str) -> Dict[int, str]:
        """Get mapping from roster_id to team display name."""
        rosters = self.client.league_service.get_league_rosters(league_id)
        users = self.client.league_service.get_league_users(league_id)
        
        roster_to_team = {}
        for roster in rosters:
            team = next((u for u in users if u.user_id == roster.owner_id), None)
            if team:
                roster_to_team[roster.roster_id] = team.display_name
            elif roster.roster_id == 9 and league_id == "1048308938824937472":
                # Special case: Roster 9 belongs to caviar89 (mlum20) but has owner_id=None
                caviar_user = next((u for u in users if u.user_id == "1176293990462615552"), None)
                if caviar_user:
                    roster_to_team[roster.roster_id] = caviar_user.display_name
            else:
                roster_to_team[roster.roster_id] = f"Team {roster.roster_id}"
        
        return roster_to_team
    
    def _get_all_years_matchup_data(self) -> Dict[int, Dict[int, List[Dict]]]:
        """Get matchup data for all available years."""
        all_years_data = {}
        
        for year, league_id in self.league_years.items():
            try:
                print(f"Loading matchup data for {year}...")
                roster_to_team_mapping = self._get_roster_to_team_mapping(league_id)
                year_data = {}
                
                for w in range(1, 19):  # Try all 18 weeks
                    try:
                        matchups = self.get_matchups(league_id, w, 18)
                        formatted_matchups = self.format_matchups_for_display(
                            matchups, roster_to_team_mapping
                        )
                        year_data[w] = formatted_matchups
                    except Exception as e:
                        # Some weeks might not have data, especially for current/future seasons
                        year_data[w] = []
                
                all_years_data[year] = year_data
                
            except Exception as e:
                print(f"Error loading data for year {year}: {e}")
                all_years_data[year] = {}
        
        return all_years_data
    
    def _calculate_cross_year_head_to_head_records(self, all_years_data: Dict[int, Dict[int, List[Dict]]], current_team_names: List[str]) -> Dict[str, Dict[str, Dict[str, int]]]:
        """Calculate head-to-head records across all years, handling team name changes."""
        records = {}
        
        # Get all unique team names across all years
        all_team_names = set(current_team_names)
        for year_data in all_years_data.values():
            for week_data in year_data.values():
                for matchup in week_data:
                    for team in matchup.get('teams', []):
                        all_team_names.add(team['name'])
        
        all_team_names = sorted(list(all_team_names))
        
        # Initialize records structure for all teams
        for team in all_team_names:
            records[team] = {}
            for opponent in all_team_names:
                if team != opponent:
                    records[team][opponent] = {'wins': 0, 'losses': 0, 'ties': 0}
        
        # Process all matchups across all years
        for year, year_data in all_years_data.items():
            for week, matchups in year_data.items():
                for matchup in matchups:
                    if len(matchup.get('teams', [])) == 2:
                        team1, team2 = matchup['teams']
                        team1_name = team1['name']
                        team2_name = team2['name']
                        
                        if team1_name in records and team2_name in records:
                            if team1['score'] > team2['score']:
                                records[team1_name][team2_name]['wins'] += 1
                                records[team2_name][team1_name]['losses'] += 1
                            elif team2['score'] > team1['score']:
                                records[team2_name][team1_name]['wins'] += 1
                                records[team1_name][team2_name]['losses'] += 1
                            else:
                                records[team1_name][team2_name]['ties'] += 1
                                records[team2_name][team1_name]['ties'] += 1
        
        # Filter to only return records for current year team names
        filtered_records = {}
        for team in current_team_names:
            if team in records:
                filtered_records[team] = {}
                for opponent in current_team_names:
                    if opponent != team and opponent in records[team]:
                        filtered_records[team][opponent] = records[team][opponent]
        
        return filtered_records