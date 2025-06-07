from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json
import os
from jinja2 import Environment, FileSystemLoader
from transaction_service import TransactionService
from player_service import PlayerService
from team_service import TeamService


class TradeVisualizationService:
    def __init__(self, sleeper_api):
        self.sleeper_api = sleeper_api
        self.transaction_service = TransactionService(sleeper_api)
        self.player_service = PlayerService()
        self.team_service = TeamService()
        
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

    def get_comprehensive_player_journey(self, league_id: str, player_name: str) -> Dict[str, Any]:
        """Track a specific player's complete history including draft, FA, and trades"""
        
        # Get all transactions (not just trades) to track complete history
        all_transactions = self.transaction_service.get_all_historical_transactions(league_id)
        
        journey = {
            'player_name': player_name,
            'total_trades': 0,
            'timeline': [],
            'teams_involved': set(),
            'current_team': None,
            'acquisition_history': [],
            'trade_partners': {},
            'draft_info': None
        }
        
        # Get roster mapping
        rosters = self.sleeper_api.league_service.get_league_rosters(league_id)
        users = self.sleeper_api.league_service.get_league_users(league_id)
        roster_to_team = {}
        for roster in rosters:
            team = next((u for u in users if u.user_id == roster.owner_id), None)
            if team:
                roster_to_team[roster.roster_id] = team.display_name
        
        # Look for player in all transactions
        player_transactions = []
        formatted_player_name = self.player_service.format_player_name(player_name)
        
        for transaction in all_transactions:
            transaction_involves_player = False
            
            # Check adds/drops
            if transaction.get('adds'):
                for player_id, roster_id in transaction['adds'].items():
                    if self.player_service.get_player_name(player_id) == formatted_player_name:
                        transaction_involves_player = True
                        break
            
            if not transaction_involves_player and transaction.get('drops'):
                for player_id, roster_id in transaction['drops'].items():
                    if self.player_service.get_player_name(player_id) == formatted_player_name:
                        transaction_involves_player = True
                        break
            
            if transaction_involves_player:
                player_transactions.append(transaction)
        
        # Sort by timestamp
        player_transactions.sort(key=lambda x: x.get('created', 0))
        
        # Process each transaction
        for i, transaction in enumerate(player_transactions):
            transaction_type = transaction.get('type', 'unknown')
            
            if transaction_type == 'trade':
                journey['total_trades'] += 1
                
                # Find what happened to the player in this trade
                from_team = None
                to_team = None
                trade_assets = {'received_with': [], 'given_for': []}
                
                # Find player movement
                if transaction.get('adds') and transaction.get('drops'):
                    for player_id in transaction['adds']:
                        if self.player_service.get_player_name(player_id) == formatted_player_name:
                            to_roster_id = transaction['adds'][player_id]
                            from_roster_id = transaction['drops'][player_id]
                            
                            to_team = roster_to_team.get(to_roster_id, f"Team {to_roster_id}")
                            from_team = roster_to_team.get(from_roster_id, f"Team {from_roster_id}")
                            break
                
                # Find what the player was traded for
                if to_team and from_team:
                    # Get other assets in the trade
                    for player_id in transaction.get('adds', {}):
                        if self.player_service.get_player_name(player_id) != formatted_player_name:
                            receiving_roster = transaction['adds'][player_id]
                            if roster_to_team.get(receiving_roster) == from_team:
                                # This asset went to the team that gave up our player
                                trade_assets['given_for'].append({
                                    'type': 'player',
                                    'name': self.player_service.get_player_name(player_id)
                                })
                    
                    # Check draft picks
                    for pick in transaction.get('draft_picks', []):
                        pick_receiver = roster_to_team.get(pick['owner_id'])
                        if pick_receiver == from_team:
                            trade_assets['given_for'].append({
                                'type': 'pick',
                                'name': f"{pick['round']} round {pick['season']}"
                            })
                
                timeline_entry = {
                    'type': 'trade',
                    'date': self._format_timestamp(transaction.get('created', 0)),
                    'from_team': from_team,
                    'to_team': to_team,
                    'trade_details': trade_assets,
                    'trade_number': journey['total_trades']
                }
                
                journey['timeline'].append(timeline_entry)
                journey['teams_involved'].add(from_team)
                journey['teams_involved'].add(to_team)
                journey['current_team'] = to_team
                
                # Track trade partners
                if from_team and to_team:
                    partner = to_team if journey.get('current_team') == from_team else from_team
                    if partner not in journey['trade_partners']:
                        journey['trade_partners'][partner] = 0
                    journey['trade_partners'][partner] += 1
            
            elif transaction_type == 'free_agent':
                # Free agent pickup
                to_team = None
                if transaction.get('adds'):
                    for player_id, roster_id in transaction['adds'].items():
                        if self.player_service.get_player_name(player_id) == formatted_player_name:
                            to_team = roster_to_team.get(roster_id, f"Team {roster_id}")
                            break
                
                if to_team:
                    timeline_entry = {
                        'type': 'free_agent',
                        'date': self._format_timestamp(transaction.get('created', 0)),
                        'from_team': 'Free Agency',
                        'to_team': to_team,
                        'trade_details': None
                    }
                    journey['timeline'].append(timeline_entry)
                    journey['teams_involved'].add(to_team)
                    journey['current_team'] = to_team
            
            elif transaction_type == 'waiver':
                # Waiver claim
                to_team = None
                if transaction.get('adds'):
                    for player_id, roster_id in transaction['adds'].items():
                        if self.player_service.get_player_name(player_id) == formatted_player_name:
                            to_team = roster_to_team.get(roster_id, f"Team {roster_id}")
                            break
                
                if to_team:
                    timeline_entry = {
                        'type': 'waiver',
                        'date': self._format_timestamp(transaction.get('created', 0)),
                        'from_team': 'Waivers',
                        'to_team': to_team,
                        'trade_details': None
                    }
                    journey['timeline'].append(timeline_entry)
                    journey['teams_involved'].add(to_team)
                    journey['current_team'] = to_team
        
        journey['teams_involved'] = list(journey['teams_involved'])
        
        return journey
    
    def _format_timestamp(self, timestamp: int) -> str:
        """Format timestamp to readable date"""
        try:
            from datetime import datetime
            return datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %I:%M %p')
        except:
            return 'Unknown date'

    def get_trade_network_data(self, league_id: str) -> Dict[str, Any]:
        """Generate network graph data showing trade relationships between teams"""
        trades = self.transaction_service.get_trades(league_id)
        
        network = {
            'nodes': {},  # team_id: {name, trade_count, total_players_acquired, total_players_given}
            'edges': {},  # (team1, team2): {weight, trades, players_exchanged}
            'timeline': [],
            'most_active_traders': [],
            'biggest_trades': []
        }
        
        # Process each trade
        for trade in trades:
            teams_in_trade = set()
            
            # Extract teams from received side (players)
            for player_data in trade.get('received', {}).get('players', []):
                team_name = player_data['team']
                teams_in_trade.add(team_name)
                
                if team_name not in network['nodes']:
                    network['nodes'][team_name] = {
                        'name': team_name,
                        'trade_count': 0,
                        'players_acquired': 0,
                        'players_given': 0,
                        'draft_picks_acquired': 0,
                        'draft_picks_given': 0
                    }
                
                network['nodes'][team_name]['players_acquired'] += 1
            
            # Extract teams from given side (players)
            for player_data in trade.get('given', {}).get('players', []):
                team_name = player_data['team']
                teams_in_trade.add(team_name)
                
                if team_name not in network['nodes']:
                    network['nodes'][team_name] = {
                        'name': team_name,
                        'trade_count': 0,
                        'players_acquired': 0,
                        'players_given': 0,
                        'draft_picks_acquired': 0,
                        'draft_picks_given': 0
                    }
                
                network['nodes'][team_name]['players_given'] += 1
            
            # Extract teams from draft picks
            for pick_data in trade.get('received', {}).get('draft_picks', []):
                from_team = pick_data.get('from_team')
                to_team = pick_data.get('to_team')
                
                if from_team:
                    teams_in_trade.add(from_team)
                    if from_team not in network['nodes']:
                        network['nodes'][from_team] = {
                            'name': from_team,
                            'trade_count': 0,
                            'players_acquired': 0,
                            'players_given': 0,
                            'draft_picks_acquired': 0,
                            'draft_picks_given': 0
                        }
                    network['nodes'][from_team]['draft_picks_given'] += 1
                
                if to_team:
                    teams_in_trade.add(to_team)
                    if to_team not in network['nodes']:
                        network['nodes'][to_team] = {
                            'name': to_team,
                            'trade_count': 0,
                            'players_acquired': 0,
                            'players_given': 0,
                            'draft_picks_acquired': 0,
                            'draft_picks_given': 0
                        }
                    network['nodes'][to_team]['draft_picks_acquired'] += 1
            
            # Update trade count for all teams involved
            teams_list = list(teams_in_trade)
            for team_name in teams_list:
                network['nodes'][team_name]['trade_count'] += 1
            
            # Create edges between trading partners
            for i, team1 in enumerate(teams_list):
                for team2 in teams_list[i+1:]:
                    edge_key = tuple(sorted([team1, team2]))
                    
                    if edge_key not in network['edges']:
                        network['edges'][edge_key] = {
                            'weight': 0,
                            'trades': [],
                            'total_players': 0,
                            'total_picks': 0
                        }
                    
                    network['edges'][edge_key]['weight'] += 1
                    network['edges'][edge_key]['trades'].append({
                        'date': trade['date'],
                        'details': self._extract_trade_details(trade)
                    })
                    
                    # Count total assets in this trade
                    network['edges'][edge_key]['total_players'] += len(trade.get('received', {}).get('players', [])) + len(trade.get('given', {}).get('players', []))
                    network['edges'][edge_key]['total_picks'] += len(trade.get('received', {}).get('draft_picks', []))
        
        # Calculate most active traders
        network['most_active_traders'] = sorted(
            network['nodes'].items(),
            key=lambda x: x[1]['trade_count'],
            reverse=True
        )[:5]
        
        return network

    def get_team_trade_matrix(self, league_id: str) -> Dict[str, Any]:
        """Generate team-to-team trade frequency matrix"""
        trades = self.transaction_service.get_trades(league_id)
        
        # Get all teams involved in trading
        all_teams = set()
        for trade in trades:
            teams = self._get_teams_from_trade(trade)
            all_teams.update(teams)
        
        all_teams = sorted(list(all_teams))
        
        # Initialize matrix
        trade_matrix = {}
        for team1 in all_teams:
            trade_matrix[team1] = {}
            for team2 in all_teams:
                trade_matrix[team1][team2] = 0
        
        # Count trades between each pair of teams
        for trade in trades:
            teams = self._get_teams_from_trade(trade)
            
            # For each pair of teams in this trade
            for i, team1 in enumerate(teams):
                for team2 in teams[i+1:]:
                    trade_matrix[team1][team2] += 1
                    trade_matrix[team2][team1] += 1  # Make matrix symmetric
        
        return {
            'teams': all_teams,
            'matrix': trade_matrix,
            'total_trades': len(trades)
        }

    def get_league_trade_timeline(self, league_id: str) -> Dict[str, Any]:
        """Generate chronological timeline of all trades with details"""
        trades = self.transaction_service.get_trades(league_id)
        
        timeline = {
            'trades': [],
            'stats': {
                'total_trades': len(trades),
                'total_players_traded': 0,
                'total_picks_traded': 0,
                'most_active_month': None,
                'trade_frequency': {}
            },
            'monthly_breakdown': {},
            'busiest_periods': []
        }
        
        # Sort trades by date
        sorted_trades = sorted(trades, key=lambda x: x.get('timestamp', 0))
        
        for trade in sorted_trades:
            # Extract month for frequency analysis
            try:
                trade_date = datetime.fromtimestamp(trade.get('timestamp', 0) / 1000)
                month_key = trade_date.strftime('%Y-%m')
                
                if month_key not in timeline['monthly_breakdown']:
                    timeline['monthly_breakdown'][month_key] = 0
                timeline['monthly_breakdown'][month_key] += 1
                
            except (ValueError, OSError):
                month_key = 'unknown'
            
            # Count assets
            players_count = len(trade.get('received', {}).get('players', [])) + len(trade.get('given', {}).get('players', []))
            picks_count = len(trade.get('received', {}).get('draft_picks', []))
            
            timeline['stats']['total_players_traded'] += players_count
            timeline['stats']['total_picks_traded'] += picks_count
            
            # Create detailed trade entry
            trade_entry = {
                'date': trade['date'],
                'timestamp': trade.get('timestamp', 0),
                'teams_involved': self._get_teams_from_trade(trade),
                'players_count': players_count,
                'picks_count': picks_count,
                'trade_details': self._extract_trade_details(trade),
                'trade_summary': self._generate_trade_summary(trade)
            }
            
            timeline['trades'].append(trade_entry)
        
        # Find most active month
        if timeline['monthly_breakdown']:
            timeline['stats']['most_active_month'] = max(
                timeline['monthly_breakdown'].items(),
                key=lambda x: x[1]
            )[0]
        
        return timeline

    def generate_trade_visualization_html(self, league_id: str, visualization_type: str = 'all') -> str:
        """Generate complete HTML visualization for trades"""
        
        # Collect all data
        network_data = self.get_trade_network_data(league_id)
        timeline_data = self.get_league_trade_timeline(league_id)
        player_counts = self.transaction_service.get_player_trade_counts(league_id)
        trade_matrix = self.get_team_trade_matrix(league_id)
        
        # Convert tuple keys to strings for JSON serialization
        network_data_serializable = {
            'nodes': network_data['nodes'],
            'edges': {str(k): v for k, v in network_data['edges'].items()},
            'timeline': network_data['timeline'],
            'most_active_traders': network_data['most_active_traders'],
            'biggest_trades': network_data['biggest_trades']
        }
        
        # Get most traded players
        most_traded_players = sorted(
            player_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        template_data = {
            'league_id': league_id,
            'network_data': network_data_serializable,
            'timeline_data': timeline_data,
            'most_traded_players': most_traded_players,
            'trade_matrix': trade_matrix,
            'visualization_type': visualization_type,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        template = self.jinja_env.get_template('trade_visualization.html')
        return template.render(**template_data)

    def save_trade_visualization(self, league_id: str, output_path: Optional[str] = None) -> str:
        """Save trade visualization to HTML file"""
        if not output_path:
            output_path = f'trade_visualization_league_{league_id}.html'
        
        html_content = self.generate_trade_visualization_html(league_id)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path

    def _extract_trade_details(self, trade: Dict[str, Any]) -> Dict[str, Any]:
        """Extract comprehensive trade details using the correct team_assets structure"""
        details = {
            'teams': [],
            'total_players': 0,
            'total_picks': 0,
            'trade_type': 'standard'
        }
        
        # Use the team_assets structure if available (new format)
        if 'team_assets' in trade:
            team_assets = trade['team_assets']
            
            for team_name, assets in team_assets.items():
                receives_players = [asset for asset in assets.get('receives', []) if asset.get('type') not in ['draft_pick', 'faab'] and asset.get('player')]
                gives_players = [asset for asset in assets.get('gives', []) if asset.get('type') not in ['draft_pick', 'faab'] and asset.get('player')]
                receives_picks = [asset for asset in assets.get('receives', []) if asset.get('type') == 'draft_pick']
                gives_picks = [asset for asset in assets.get('gives', []) if asset.get('type') == 'draft_pick']
                receives_faab = [asset for asset in assets.get('receives', []) if asset.get('type') == 'faab']
                gives_faab = [asset for asset in assets.get('gives', []) if asset.get('type') == 'faab']
                
                team_info = {
                    'team': team_name,
                    'receives': {
                        'players': receives_players,
                        'draft_picks': receives_picks,
                        'faab': receives_faab
                    },
                    'gives': {
                        'players': gives_players,
                        'draft_picks': gives_picks,
                        'faab': gives_faab
                    }
                }
                
                details['teams'].append(team_info)
                details['total_players'] += len(receives_players) + len(gives_players)
                details['total_picks'] += len(receives_picks) + len(gives_picks)
        
        else:
            # Fallback to old format (for backward compatibility)
            team_data = {}
            
            # Process received players
            for player_data in trade.get('received', {}).get('players', []):
                team_name = player_data['team']
                if team_name not in team_data:
                    team_data[team_name] = {'receives': {'players': [], 'draft_picks': []}, 'gives': {'players': [], 'draft_picks': []}}
                team_data[team_name]['receives']['players'].append(player_data)
            
            # Process given players  
            for player_data in trade.get('given', {}).get('players', []):
                team_name = player_data['team']
                if team_name not in team_data:
                    team_data[team_name] = {'receives': {'players': [], 'draft_picks': []}, 'gives': {'players': [], 'draft_picks': []}}
                team_data[team_name]['gives']['players'].append(player_data)
            
            # Process draft picks
            for pick_data in trade.get('received', {}).get('draft_picks', []):
                to_team = pick_data.get('to_team')
                from_team = pick_data.get('from_team')
                
                if to_team and to_team not in team_data:
                    team_data[to_team] = {'receives': {'players': [], 'draft_picks': []}, 'gives': {'players': [], 'draft_picks': []}}
                if to_team:
                    team_data[to_team]['receives']['draft_picks'].append(pick_data)
                
                if from_team and from_team not in team_data:
                    team_data[from_team] = {'receives': {'players': [], 'draft_picks': []}, 'gives': {'players': [], 'draft_picks': []}}
                if from_team:
                    team_data[from_team]['gives']['draft_picks'].append(pick_data)
            
            # Convert to list format
            for team_name, data in team_data.items():
                team_info = {
                    'team': team_name,
                    'receives': data['receives'],
                    'gives': data['gives']
                }
                details['teams'].append(team_info)
                details['total_players'] += len(data['receives']['players']) + len(data['gives']['players'])
                details['total_picks'] += len(data['receives']['draft_picks']) + len(data['gives']['draft_picks'])
        
        # Determine trade type
        if details['total_players'] == 0:
            details['trade_type'] = 'picks_only'
        elif details['total_picks'] == 0:
            details['trade_type'] = 'players_only'
        else:
            details['trade_type'] = 'mixed'
        
        return details

    def _get_assets_in_trade(self, trade: Dict[str, Any], player_name: str) -> Dict[str, Any]:
        """Get all assets involved in a trade with a specific player"""
        assets = {
            'with_player': {'players': [], 'picks': []},
            'counter_assets': {'players': [], 'picks': []}
        }
        
        player_side = None
        player_team = None
        
        # Find which side the player is on
        for team_data in trade.get('received', {}).get('teams', []):
            for player in team_data.get('players', []):
                if self.player_service.format_player_name(player['player']) == player_name:
                    player_side = 'received'
                    player_team = team_data['team']
                    assets['with_player']['players'] = team_data.get('players', [])
                    assets['with_player']['picks'] = team_data.get('draft_picks', [])
                    break
        
        if not player_side:
            for team_data in trade.get('given', {}).get('teams', []):
                for player in team_data.get('players', []):
                    if self.player_service.format_player_name(player['player']) == player_name:
                        player_side = 'given'
                        player_team = team_data['team']
                        assets['with_player']['players'] = team_data.get('players', [])
                        assets['with_player']['picks'] = team_data.get('draft_picks', [])
                        break
        
        # Get counter assets from opposite side
        opposite_side = 'given' if player_side == 'received' else 'received'
        for team_data in trade.get(opposite_side, {}).get('teams', []):
            assets['counter_assets']['players'].extend(team_data.get('players', []))
            assets['counter_assets']['picks'].extend(team_data.get('draft_picks', []))
        
        return assets

    def _get_teams_from_trade(self, trade: Dict[str, Any]) -> List[str]:
        """Extract all team names involved in a trade"""
        teams = set()
        
        # Get teams from received players
        for player_data in trade.get('received', {}).get('players', []):
            teams.add(player_data['team'])
        
        # Get teams from given players
        for player_data in trade.get('given', {}).get('players', []):
            teams.add(player_data['team'])
        
        # Get teams from draft picks
        for pick_data in trade.get('received', {}).get('draft_picks', []):
            if pick_data.get('from_team'):
                teams.add(pick_data['from_team'])
            if pick_data.get('to_team'):
                teams.add(pick_data['to_team'])
        
        return list(teams)

    def _generate_trade_summary(self, trade: Dict[str, Any]) -> str:
        """Generate human-readable trade summary"""
        summary_parts = []
        
        # Group by teams
        team_summaries = {}
        
        # Process received players
        for player_data in trade.get('received', {}).get('players', []):
            team_name = player_data['team']
            if team_name not in team_summaries:
                team_summaries[team_name] = {'received': [], 'given': []}
            team_summaries[team_name]['received'].append(player_data['player'])
        
        # Process given players
        for player_data in trade.get('given', {}).get('players', []):
            team_name = player_data['team']
            if team_name not in team_summaries:
                team_summaries[team_name] = {'received': [], 'given': []}
            team_summaries[team_name]['given'].append(player_data['player'])
        
        # Process draft picks
        for pick_data in trade.get('received', {}).get('draft_picks', []):
            from_team = pick_data.get('from_team')
            to_team = pick_data.get('to_team')
            pick_desc = f"{pick_data['round']} round {pick_data['season']}"
            
            if from_team:
                if from_team not in team_summaries:
                    team_summaries[from_team] = {'received': [], 'given': []}
                team_summaries[from_team]['given'].append(pick_desc)
            
            if to_team:
                if to_team not in team_summaries:
                    team_summaries[to_team] = {'received': [], 'given': []}
                team_summaries[to_team]['received'].append(pick_desc)
        
        # Build summary string
        for team_name, data in team_summaries.items():
            team_parts = []
            if data['received']:
                team_parts.append(f"received: {', '.join(data['received'])}")
            if data['given']:
                team_parts.append(f"gave: {', '.join(data['given'])}")
            
            if team_parts:
                summary_parts.append(f"{team_name} {' and '.join(team_parts)}")
        
        return " | ".join(summary_parts)