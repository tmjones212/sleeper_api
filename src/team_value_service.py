from typing import List, Dict, Any, Optional
import os
import json
from datetime import datetime
import webbrowser
from jinja2 import Environment, FileSystemLoader
from ktc_service import KTCService
from league_service import LeagueService

class TeamValueService:
    def __init__(self, client):
        self.client = client
        self.env = Environment(loader=FileSystemLoader('templates'))
        self.ktc_service = KTCService()
        
    def get_team_values(self, league_id: str, use_qb_for_superflex_if_possible: bool = True) -> List[Dict[str, Any]]:
        """Get all teams with their players and KTC values."""
        # Get league data
        league = self.client.league_service.get_league(league_id, fetch_all=True)
        
        # Get KTC data for all players
        ktc_data = self.ktc_service.get_player_values()
        
        # Create a dictionary for quick KTC value lookup by player name
        ktc_value_map = {
            player.get('name', '').upper(): player.get('value', 0)
            for player in ktc_data
        }
        
        team_values = []
        
        # Process each team
        for team in league.teams:
            if not team.roster:
                continue
                
            team_data = {
                'team_name': team.display_name,
                'user_id': team.user_id,
                'players': [],
                'total_value': 0,
                'position_values': {
                    'QB': 0,
                    'RB': 0,
                    'WR': 0,
                    'TE': 0
                },
                'total_age': 0,
                'player_count': 0,
                'avg_age': 0,
                'starter_value': 0,
                'avg_starter_value': 0
            }
            
            # Process players
            for player_id in team.roster.players:
                player_name = self.client.player_service.get_player_name(player_id)
                player_position = self.client.player_service.get_player_position(player_id)
                player_age = self.client.player_service.get_player_age(player_id)
                
                # Find KTC value for this player
                ktc_value = 0
                for ktc_player in ktc_data:
                    if self._match_player_name(ktc_player.get('name', ''), player_name):
                        ktc_value = ktc_player.get('value', 0)
                        break
                
                team_data['players'].append({
                    'name': player_name,
                    'position': player_position,
                    'ktc_value': ktc_value,
                    'age': player_age
                })
                
                team_data['total_value'] += ktc_value
                
                # Add to position totals if it's one of our tracked positions
                if player_position in team_data['position_values']:
                    team_data['position_values'][player_position] += ktc_value
                
                # Track age for average calculation only if value is 2000+
                if player_age and ktc_value >= 2000:
                    team_data['total_age'] += player_age
                    team_data['player_count'] += 1
            
            # Calculate average age
            if team_data['player_count'] > 0:
                team_data['avg_age'] = round(team_data['total_age'] / team_data['player_count'], 1)
            
            # Sort players by KTC value (highest first)
            team_data['players'].sort(key=lambda x: x['ktc_value'], reverse=True)
            
            # Calculate starter value
            starter_value, avg_starter_value = self._calculate_starter_value(
                team_data['players'], 
                league.roster_positions,
                use_qb_for_superflex_if_possible
            )
            team_data['starter_value'] = starter_value
            team_data['avg_starter_value'] = avg_starter_value
            
            team_values.append(team_data)
        
        # Sort teams by total value (highest first)
        team_values.sort(key=lambda x: x['total_value'], reverse=True)
        
        return team_values
    
    def _calculate_starter_value(self, players: List[Dict[str, Any]], roster_positions: List[str], 
                                use_qb_for_superflex_if_possible: bool) -> tuple:
        """Calculate the value of starting players based on league roster positions."""
        # Create position-specific player lists sorted by value
        qbs = sorted([p for p in players if p['position'] == 'QB'], key=lambda x: x['ktc_value'], reverse=True)
        rbs = sorted([p for p in players if p['position'] == 'RB'], key=lambda x: x['ktc_value'], reverse=True)
        wrs = sorted([p for p in players if p['position'] == 'WR'], key=lambda x: x['ktc_value'], reverse=True)
        tes = sorted([p for p in players if p['position'] == 'TE'], key=lambda x: x['ktc_value'], reverse=True)
        
        # Filter out bench and defensive positions
        starter_positions = [pos for pos in roster_positions if pos not in ['BN', 'IDP_FLEX', 'K', 'LB', 'DB', 'DL', 'DE', 'DT', 'CB', 'S']]
        
        # Track used players to avoid double-counting
        used_players = set()
        starters = []
        
        # First, fill required positions
        for pos in starter_positions:
            if pos == 'QB':
                if qbs and len(qbs) > 0:
                    for i, player in enumerate(qbs):
                        if player['name'] not in used_players:
                            starters.append(player)
                            used_players.add(player['name'])
                            qbs.pop(i)
                            break
            elif pos == 'RB':
                if rbs and len(rbs) > 0:
                    for i, player in enumerate(rbs):
                        if player['name'] not in used_players:
                            starters.append(player)
                            used_players.add(player['name'])
                            rbs.pop(i)
                            break
            elif pos == 'WR':
                if wrs and len(wrs) > 0:
                    for i, player in enumerate(wrs):
                        if player['name'] not in used_players:
                            starters.append(player)
                            used_players.add(player['name'])
                            wrs.pop(i)
                            break
            elif pos == 'TE':
                if tes and len(tes) > 0:
                    for i, player in enumerate(tes):
                        if player['name'] not in used_players:
                            starters.append(player)
                            used_players.add(player['name'])
                            tes.pop(i)
                            break
            elif pos == 'FLEX':
                # For FLEX, find the highest value player among RB, WR, TE
                flex_options = []
                if rbs: flex_options.extend(rbs)
                if wrs: flex_options.extend(wrs)
                if tes: flex_options.extend(tes)
                
                flex_options = [p for p in flex_options if p['name'] not in used_players]
                if flex_options:
                    best_flex = max(flex_options, key=lambda x: x['ktc_value'])
                    starters.append(best_flex)
                    used_players.add(best_flex['name'])
                    
                    # Remove the used player from its position list
                    if best_flex['position'] == 'RB' and best_flex in rbs:
                        rbs.remove(best_flex)
                    elif best_flex['position'] == 'WR' and best_flex in wrs:
                        wrs.remove(best_flex)
                    elif best_flex['position'] == 'TE' and best_flex in tes:
                        tes.remove(best_flex)
            
            elif pos == 'SUPER_FLEX':
                # For SUPER_FLEX, find the highest value player among QB, RB, WR, TE
                # If use_qb_for_superflex_if_possible is True and a QB is available, use it
                if use_qb_for_superflex_if_possible and qbs and len(qbs) > 0:
                    for i, player in enumerate(qbs):
                        if player['name'] not in used_players:
                            starters.append(player)
                            used_players.add(player['name'])
                            qbs.pop(i)
                            break
                else:
                    # Otherwise, find the best available player
                    superflex_options = []
                    if qbs: superflex_options.extend(qbs)
                    if rbs: superflex_options.extend(rbs)
                    if wrs: superflex_options.extend(wrs)
                    if tes: superflex_options.extend(tes)
                    
                    superflex_options = [p for p in superflex_options if p['name'] not in used_players]
                    if superflex_options:
                        best_superflex = max(superflex_options, key=lambda x: x['ktc_value'])
                        starters.append(best_superflex)
                        used_players.add(best_superflex['name'])
                        
                        # Remove the used player from its position list
                        if best_superflex['position'] == 'QB' and best_superflex in qbs:
                            qbs.remove(best_superflex)
                        elif best_superflex['position'] == 'RB' and best_superflex in rbs:
                            rbs.remove(best_superflex)
                        elif best_superflex['position'] == 'WR' and best_superflex in wrs:
                            wrs.remove(best_superflex)
                        elif best_superflex['position'] == 'TE' and best_superflex in tes:
                            tes.remove(best_superflex)
        
        # Calculate total starter value
        starter_value = sum(player['ktc_value'] for player in starters)
        
        # Calculate average starter value
        avg_starter_value = round(starter_value / len(starters), 1) if starters else 0
        
        return starter_value, avg_starter_value
    
    def _match_player_name(self, ktc_name: str, sleeper_name: str) -> bool:
        """Match player names between KTC and Sleeper formats."""
        ktc_name = self.client.player_service.format_player_name(ktc_name)
        sleeper_name = self.client.player_service.format_player_name(sleeper_name)
        return ktc_name == sleeper_name
    
    def generate_team_value_report(self, league_id: str, output_path: str = "team_values.html", use_qb_for_superflex_if_possible: bool = True):
        """Generate an HTML report of team values."""
        team_values = self.get_team_values(league_id, use_qb_for_superflex_if_possible)
        league = self.client.league_service.get_league(league_id)
        
        # Create template data
        template_data = {
            'league_name': league.name,
            'teams': team_values,
            'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Render template
        template = self.env.get_template('team_values.html')
        html_content = template.render(**template_data)
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Open in browser
        webbrowser.open('file://' + os.path.abspath(output_path))
        
        return output_path


if __name__ == "__main__":
    from client import SleeperAPI
    
    client = SleeperAPI()
    value_service = TeamValueService(client)
    
    # 2024 league ID
    league_id = "1181025001438806016"
    
    html_path = value_service.generate_team_value_report(league_id)
    print(f"Team value report generated at: {html_path}")