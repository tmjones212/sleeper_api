from typing import List, Dict, Any, Optional
import os
import json
from datetime import datetime
import webbrowser
from jinja2 import Environment, FileSystemLoader
import sys

# Import KTC service
try:
    from ktc_service import KTCService
except ImportError:
    try:
        from src.ktc_service import KTCService
    except ImportError:
        print("Warning: Could not import KTCService")
        KTCService = None

class TeamValueService:
    def __init__(self, client):
        self.client = client
        self.env = Environment(loader=FileSystemLoader('templates'))
        # Create KTC service instance
        self.ktc_service = KTCService() if KTCService else None
        
    def get_team_values(self, league_id: str, use_qb_for_superflex_if_possible: bool = True) -> List[Dict[str, Any]]:
        """Get all teams with their players and KTC values."""
        # Get league data
        league = self.client.league_service.get_league(league_id, fetch_all=True)
        
        # Get KTC data - try different methods based on environment
        ktc_value_map = self._get_ktc_values()
        
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
                'avg_starter_value': 0,
                'starters': []
            }
            
            # Process players
            for player_id in team.roster.players:
                player_name = self.client.player_service.get_player_name(player_id)
                if not player_name:
                    continue
                    
                player_position = self.client.player_service.get_player_position(player_id)
                if not player_position:
                    continue
                
                player_age = self.client.player_service.get_player_age(player_id) or 0
                
                # Look up KTC value and round to integer
                ktc_value = round(ktc_value_map.get(player_name.upper(), 0))
                
                # Add to team total if it's a fantasy-relevant position
                if player_position in ['QB', 'RB', 'WR', 'TE']:
                    team_data['total_value'] += ktc_value
                    team_data['position_values'][player_position] += ktc_value
                
                # Add to age calculations
                if player_age > 0:
                    team_data['total_age'] += player_age
                    team_data['player_count'] += 1
                
                # Create player data
                player_data = {
                    'name': player_name,
                    'position': player_position,
                    'age': player_age,
                    'ktc_value': ktc_value,  # Already rounded
                    'is_starter': False,
                    'starter_position': ''
                }
                
                team_data['players'].append(player_data)
            
            # Calculate average age and round to integer
            if team_data['player_count'] > 0:
                team_data['avg_age'] = round(team_data['total_age'] / team_data['player_count'])
            
            # Determine starters based on league settings
            starters = self._determine_starters(team_data['players'], league, use_qb_for_superflex_if_possible)
            team_data['starters'] = starters
            
            # Calculate starter value
            starter_value = sum(starter['ktc_value'] for starter in starters)
            team_data['starter_value'] = starter_value
            
            # Calculate average starter value and round to integer
            if starters:
                team_data['avg_starter_value'] = round(starter_value / len(starters))
            
            # Round all position values to integers
            for position in team_data['position_values']:
                team_data['position_values'][position] = round(team_data['position_values'][position])
            
            team_values.append(team_data)
        
        return team_values
        
    def _get_ktc_values(self):
        """Get KTC values using the appropriate method for the current environment."""
        # Check if we're on PythonAnywhere
        on_pythonanywhere = 'PYTHONANYWHERE_SITE' in os.environ
        
        if on_pythonanywhere:
            # On PythonAnywhere, load from file
            return self._load_ktc_values_from_file()
        else:
            # Locally, use the KTC service
            return self._get_ktc_values_from_service()
    
    def _get_ktc_values_from_service(self):
        """Get KTC values using the KTC service."""
        ktc_value_map = {}
        
        if self.ktc_service:
            try:
                ktc_data = self.ktc_service.get_player_values()
                
                # Create a dictionary for quick KTC value lookup by player name
                ktc_value_map = {
                    player.get('name', '').upper(): player.get('value', 0)
                    for player in ktc_data
                }
            except Exception as e:
                print(f"Error getting KTC data from service: {e}")
        
        return ktc_value_map
    
    def _load_ktc_values_from_file(self):
        """Load KTC values from a JSON file."""
        ktc_value_map = {}
        
        # Define possible file paths
        file_paths = [
            'data/ktc_values.json',
            'src/data/ktc_values.json',
            os.path.join(os.path.dirname(__file__), 'data', 'ktc_values.json'),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'ktc_values.json')
        ]
        
        # Try each path
        for file_path in file_paths:
            try:
                with open(file_path, 'r') as f:
                    ktc_data = json.load(f)
                    
                    # Create a dictionary for quick KTC value lookup by player name
                    ktc_value_map = {
                        player.get('name', '').upper(): player.get('value', 0)
                        for player in ktc_data
                    }
                    
                    print(f"Loaded {len(ktc_value_map)} KTC values from {file_path}")
                    return ktc_value_map
            except FileNotFoundError:
                continue
            except Exception as e:
                print(f"Error loading KTC data from {file_path}: {e}")
                continue
        
        print("Warning: Could not load KTC values from any file")
        return ktc_value_map
    
    def _determine_starters(self, players, league, use_qb_for_superflex_if_possible=True):
        """Determine which players are starters based on league settings."""
        # Make a copy of players to avoid modifying the original
        players_copy = players.copy()
        
        # Sort players by KTC value (highest first)
        players_copy.sort(key=lambda x: x['ktc_value'], reverse=True)
        
        # Get league settings
        roster_positions = league.roster_positions
        
        # Initialize starters list
        starters = []
        
        # Track which players have been assigned as starters
        assigned_players = set()
        
        # Process each roster position
        for position in roster_positions:
            # Skip bench positions
            if position == 'BN':
                continue
            
            # Find the best available player for this position
            best_player = None
            
            if position == 'QB':
                # Find best available QB
                for player in players_copy:
                    if player['position'] == 'QB' and player['name'] not in assigned_players:
                        best_player = player
                        best_player['starter_position'] = 'QB'
                        break
                    
            elif position == 'RB':
                # Find best available RB
                for player in players_copy:
                    if player['position'] == 'RB' and player['name'] not in assigned_players:
                        best_player = player
                        best_player['starter_position'] = 'RB'
                        break
                    
            elif position == 'WR':
                # Find best available WR
                for player in players_copy:
                    if player['position'] == 'WR' and player['name'] not in assigned_players:
                        best_player = player
                        best_player['starter_position'] = 'WR'
                        break
                    
            elif position == 'TE':
                # Find best available TE
                for player in players_copy:
                    if player['position'] == 'TE' and player['name'] not in assigned_players:
                        best_player = player
                        best_player['starter_position'] = 'TE'
                        break
                    
            elif position == 'FLEX':
                # Find best available RB/WR/TE
                for player in players_copy:
                    if player['position'] in ['RB', 'WR', 'TE'] and player['name'] not in assigned_players:
                        best_player = player
                        best_player['starter_position'] = 'FLEX'
                        break
                    
            elif position == 'SUPER_FLEX' or position == 'SUPERFLEX':
                # For superflex, prefer QB if specified
                if use_qb_for_superflex_if_possible:
                    # Try to find a QB first
                    for player in players_copy:
                        if player['position'] == 'QB' and player['name'] not in assigned_players:
                            best_player = player
                            best_player['starter_position'] = 'SUPER_FLEX'
                            break
                            
                # If no QB or not preferring QB, find best available QB/RB/WR/TE
                if not best_player:
                    for player in players_copy:
                        if player['position'] in ['QB', 'RB', 'WR', 'TE'] and player['name'] not in assigned_players:
                            best_player = player
                            best_player['starter_position'] = 'SUPER_FLEX'
                            break
            
            # If we found a player for this position, add them to starters
            if best_player:
                # Mark the player as a starter
                best_player['is_starter'] = True
                
                # Add to starters list
                starters.append(best_player.copy())
                
                # Mark as assigned
                assigned_players.add(best_player['name'])
        
        return starters
    
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

def generate_team_value_html(team_values_data):
    """Generate HTML for team values report."""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dynasty League Team Values</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            h1, h2, h3 {
                color: #2c3e50;
            }
            .team-card {
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                margin-bottom: 20px;
                padding: 20px;
                border-left: 5px solid #3498db;
            }
            .team-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 1px solid #eee;
                padding-bottom: 10px;
                margin-bottom: 15px;
            }
            .team-name {
                font-size: 24px;
                font-weight: bold;
                margin: 0;
            }
            .team-value {
                font-size: 20px;
                font-weight: bold;
                color: #3498db;
            }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-bottom: 20px;
            }
            .stat-box {
                background-color: #f8f9fa;
                padding: 10px;
                border-radius: 5px;
                text-align: center;
            }
            .stat-label {
                font-size: 14px;
                color: #7f8c8d;
                margin-bottom: 5px;
            }
            .stat-value {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
            }
            .position-values {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin-bottom: 20px;
            }
            .position-box {
                flex: 1;
                min-width: 100px;
                background-color: #f8f9fa;
                padding: 10px;
                border-radius: 5px;
                text-align: center;
            }
            .position-label {
                font-size: 14px;
                color: #7f8c8d;
            }
            .position-value {
                font-size: 18px;
                font-weight: bold;
            }
            .players-section {
                margin-top: 20px;
            }
            .section-title {
                font-size: 18px;
                margin-bottom: 10px;
                color: #2c3e50;
                border-bottom: 1px solid #eee;
                padding-bottom: 5px;
            }
            .players-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                gap: 10px;
            }
            .player-card {
                background-color: #f8f9fa;
                padding: 10px;
                border-radius: 5px;
                display: flex;
                justify-content: space-between;
            }
            .player-card.starter {
                background-color: #d4edda;
                border-left: 3px solid #28a745;
            }
            .player-info {
                flex: 1;
            }
            .player-name {
                font-weight: bold;
                margin-bottom: 2px;
            }
            .player-details {
                font-size: 12px;
                color: #6c757d;
            }
            .player-value {
                font-weight: bold;
                color: #3498db;
                margin-left: 10px;
            }
            .summary-section {
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                margin-bottom: 30px;
            }
            .summary-card {
                flex: 1;
                min-width: 300px;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                padding: 15px;
            }
            .summary-title {
                font-size: 18px;
                margin-bottom: 15px;
                color: #2c3e50;
                border-bottom: 1px solid #eee;
                padding-bottom: 5px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                padding: 8px 12px;
                text-align: left;
                border-bottom: 1px solid #eee;
            }
            th {
                background-color: #f8f9fa;
                font-weight: bold;
                color: #2c3e50;
            }
            tr:hover {
                background-color: #f5f5f5;
            }
            .sort-btn {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                cursor: pointer;
                margin-right: 10px;
                margin-bottom: 10px;
            }
            .sort-btn:hover {
                background-color: #2980b9;
            }
            .sort-controls {
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <h1>Dynasty League Team Values</h1>
        
        <div class="sort-controls">
            <button class="sort-btn" onclick="sortTeams('total')">Sort by Total Value</button>
            <button class="sort-btn" onclick="sortTeams('starter')">Sort by Starter Value</button>
            <button class="sort-btn" onclick="sortTeams('avg-starter')">Sort by Avg Starter Value</button>
            <button class="sort-btn" onclick="sortTeams('age')">Sort by Age</button>
        </div>
        
        <div class="summary-section">
            <div class="summary-card">
                <h3 class="summary-title">Team Rankings</h3>
                <table id="rankings-table">
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Team</th>
                            <th>Total Value</th>
                            <th>Starter Value</th>
                            <th>Avg Starter</th>
                            <th>Avg Age</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    # Sort teams by total value for initial display
    sorted_teams = sorted(team_values_data, key=lambda x: x['total_value'], reverse=True)
    
    # Add team rows to the summary table
    for i, team in enumerate(sorted_teams):
        html += f"""
                        <tr>
                            <td>{i+1}</td>
                            <td>{team['team_name']}</td>
                            <td>{team['total_value']}</td>
                            <td>{team['starter_value']}</td>
                            <td>{team['avg_starter_value']}</td>
                            <td>{team['avg_age']}</td>
                        </tr>
        """
    
    html += """
                    </tbody>
                </table>
            </div>
        </div>
        
        <div id="teams-container">
    """
    
    # Generate team cards
    for team in sorted_teams:
        html += f"""
        <div class="team-card" data-total="{team['total_value']}" data-starter="{team['starter_value']}" data-avg-starter="{team['avg_starter_value']}" data-age="{team['avg_age']}">
            <div class="team-header">
                <h2 class="team-name">{team['team_name']}</h2>
                <div class="team-value">Total Value: {team['total_value']}</div>
            </div>
            
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-label">Starter Value</div>
                    <div class="stat-value">{team['starter_value']}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Avg Starter Value</div>
                    <div class="stat-value">{team['avg_starter_value']}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Average Age</div>
                    <div class="stat-value">{team['avg_age']}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Player Count</div>
                    <div class="stat-value">{team['player_count']}</div>
                </div>
            </div>
            
            <div class="position-values">
                <div class="position-box">
                    <div class="position-label">QB</div>
                    <div class="position-value">{team['position_values']['QB']}</div>
                </div>
                <div class="position-box">
                    <div class="position-label">RB</div>
                    <div class="position-value">{team['position_values']['RB']}</div>
                </div>
                <div class="position-box">
                    <div class="position-label">WR</div>
                    <div class="position-value">{team['position_values']['WR']}</div>
                </div>
                <div class="position-box">
                    <div class="position-label">TE</div>
                    <div class="position-value">{team['position_values']['TE']}</div>
                </div>
            </div>
            
            <div class="players-section">
                <h3 class="section-title">Starters</h3>
                <div class="players-grid">
        """
        
        # Add starters
        for player in team['starters']:
            html += f"""
                    <div class="player-card starter">
                        <div class="player-info">
                            <div class="player-name">{player['name']} ({player['starter_position']})</div>
                            <div class="player-details">{player['position']} | Age: {player['age']}</div>
                        </div>
                        <div class="player-value">{player['ktc_value']}</div>
                    </div>
            """
        
        html += """
                </div>
            </div>
            
            <div class="players-section">
                <h3 class="section-title">Bench</h3>
                <div class="players-grid">
        """
        
        # Add bench players (non-starters)
        bench_players = [p for p in team['players'] if not p.get('is_starter', False)]
        # Sort bench by value
        bench_players = sorted(bench_players, key=lambda x: x.get('ktc_value', 0), reverse=True)
        
        for player in bench_players:
            if player.get('ktc_value', 0) > 0:  # Only show players with value
                html += f"""
                    <div class="player-card">
                        <div class="player-info">
                            <div class="player-name">{player['name']}</div>
                            <div class="player-details">{player['position']} | Age: {player['age']}</div>
                        </div>
                        <div class="player-value">{player.get('ktc_value', 0)}</div>
                    </div>
                """
        
        html += """
                </div>
            </div>
        </div>
        """
    
    # Close the container and add JavaScript for sorting
    html += """
        </div>
        
        <script>
            function sortTeams(criterion) {
                const container = document.getElementById('teams-container');
                const teams = Array.from(container.getElementsByClassName('team-card'));
                
                teams.sort((a, b) => {
                    let valueA, valueB;
                    
                    switch(criterion) {
                        case 'total':
                            valueA = parseInt(a.dataset.total);
                            valueB = parseInt(b.dataset.total);
                            break;
                        case 'starter':
                            valueA = parseInt(a.dataset.starter);
                            valueB = parseInt(b.dataset.starter);
                            break;
                        case 'avg-starter':
                            valueA = parseInt(a.dataset.avgStarter);
                            valueB = parseInt(b.dataset.avgStarter);
                            break;
                        case 'age':
                            valueA = parseInt(a.dataset.age);
                            valueB = parseInt(b.dataset.age);
                            return valueA - valueB; // Ascending for age
                    }
                    
                    return valueB - valueA; // Descending for values
                });
                
                // Remove all teams
                while (container.firstChild) {
                    container.removeChild(container.firstChild);
                }
                
                // Add sorted teams
                teams.forEach(team => {
                    container.appendChild(team);
                });
                
                // Update the rankings table
                updateRankingsTable(criterion);
            }
            
            function updateRankingsTable(criterion) {
                const table = document.getElementById('rankings-table');
                const tbody = table.getElementsByTagName('tbody')[0];
                const rows = Array.from(tbody.getElementsByTagName('tr'));
                
                // Get the column index based on criterion
                let columnIndex;
                switch(criterion) {
                    case 'total':
                        columnIndex = 2;
                        break;
                    case 'starter':
                        columnIndex = 3;
                        break;
                    case 'avg-starter':
                        columnIndex = 4;
                        break;
                    case 'age':
                        columnIndex = 5;
                        break;
                    default:
                        columnIndex = 2;
                }
                
                // Sort rows
                rows.sort((a, b) => {
                    const valueA = parseInt(a.cells[columnIndex].textContent);
                    const valueB = parseInt(b.cells[columnIndex].textContent);
                    
                    if (criterion === 'age') {
                        return valueA - valueB; // Ascending for age
                    }
                    return valueB - valueA; // Descending for values
                });
                
                // Remove all rows
                while (tbody.firstChild) {
                    tbody.removeChild(tbody.firstChild);
                }
                
                // Add sorted rows and update ranks
                rows.forEach((row, index) => {
                    row.cells[0].textContent = index + 1;
                    tbody.appendChild(row);
                });
            }
        </script>
    </body>
    </html>
    """
    
    return html

# Save the HTML to a file
def save_team_value_html(team_values_data, output_path="team_values.html"):
    html = generate_team_value_html(team_values_data)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_path

if __name__ == "__main__":
    from client import SleeperAPI
    
    client = SleeperAPI()
    value_service = TeamValueService(client)
    
    # 2024 league ID
    league_id = "1181025001438806016"
    
    html_path = value_service.generate_team_value_report(league_id)
    print(f"Team value report generated at: {html_path}")
    save_team_value_html(value_service.get_team_values(league_id), "team_values_new.html")