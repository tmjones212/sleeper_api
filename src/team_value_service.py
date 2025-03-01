from typing import List, Dict, Any, Optional
import os
import json
from datetime import datetime
import webbrowser
from jinja2 import Environment, FileSystemLoader
from ktc_service import KTCService

class TeamValueService:
    def __init__(self, client):
        self.client = client
        self.env = Environment(loader=FileSystemLoader('templates'))
        self.ktc_service = KTCService()
        
    def get_team_values(self, league_id: str) -> List[Dict[str, Any]]:
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
                'total_value': 0
            }
            
            # Process players
            for player_id in team.roster.players:
                player_name = self.client.player_service.get_player_name(player_id)
                player_position = self.client.player_service.get_player_position(player_id)
                
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
                    'image_url': self.client.player_service.get_player_image_url(player_id)
                })
                
                team_data['total_value'] += ktc_value
            
            # Sort players by KTC value (highest first)
            team_data['players'].sort(key=lambda x: x['ktc_value'], reverse=True)
            
            team_values.append(team_data)
        
        # Sort teams by total value (highest first)
        team_values.sort(key=lambda x: x['total_value'], reverse=True)
        
        return team_values
    
    def _match_player_name(self, ktc_name: str, sleeper_name: str) -> bool:
        """Match player names between KTC and Sleeper formats."""
        ktc_name = self.client.player_service.format_player_name(ktc_name)
        sleeper_name = self.client.player_service.format_player_name(sleeper_name)
        return ktc_name == sleeper_name
    
    def generate_team_value_report(self, league_id: str, output_path: str = "team_values.html"):
        """Generate an HTML report of team values."""
        team_values = self.get_team_values(league_id)
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
    league_id = "1048308938824937472"
    
    html_path = value_service.generate_team_value_report(league_id)
    print(f"Team value report generated at: {html_path}")