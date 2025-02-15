from datetime import datetime
import os
import json
from typing import List, Dict, Any

class TransactionManager:
    def __init__(self, client):
        self.client = client

    def get_all_league_transactions(self, league_id: str) -> List[Dict[str, Any]]:
        """
        Get all transactions for a league, starting from week 1 until no more transactions are found.
        Enhances transactions with team name information.
        """
        # Get league data to map roster_ids to team names
        league = self.client.league_manager.get_league(league_id, fetch_all=True)
        team_names = {team.roster.roster_id: team.display_name for team in league.teams if team.roster}
        
        all_transactions = []
        week = 1
        
        while True:
            transactions = self.client.league_manager.get_league_transactions(league_id, week)
            if not transactions:  # If no transactions are found for this week
                break
            
            # Add week number and datetime fields to each transaction
            for transaction in transactions:
                transaction['week'] = week
                
                # Add team names for adds and drops
                if transaction.get('adds'):
                    transaction['adds_teams'] = {
                        player_id: team_names.get(roster_id, f"Team {roster_id}")
                        for player_id, roster_id in transaction['adds'].items()
                    }
                
                if transaction.get('drops'):
                    transaction['drops_teams'] = {
                        player_id: team_names.get(roster_id, f"Team {roster_id}")
                        for player_id, roster_id in transaction['drops'].items()
                    }
                
                # Add team names for roster_ids array
                if transaction.get('roster_ids'):
                    transaction['roster_names'] = [
                        team_names.get(roster_id, f"Team {roster_id}")
                        for roster_id in transaction['roster_ids']
                    ]
                
                # Add status updated datetime
                if transaction.get('status_updated'):
                    dt = datetime.fromtimestamp(transaction['status_updated'] / 1000)
                    transaction['datetime'] = dt.strftime('%Y-%m-%d %I:%M %p')
                
                # Add created datetime
                if transaction.get('created'):
                    dt = datetime.fromtimestamp(transaction['created'] / 1000)
                    transaction['created_datetime'] = dt.strftime('%Y-%m-%d %I:%M %p')
            
            all_transactions.extend(transactions)
            week += 1
        
        # Sort transactions by status_updated time
        all_transactions.sort(key=lambda x: x.get('status_updated', 0))
        
        # Save to JSON file
        filename = f"data/league_{league_id}_transactions.json"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(all_transactions, f, indent=2)
        
        return all_transactions

    def get_trades(self, league_id):
        """Get and format all trades for a league."""
        # Get all transactions through league_analytics
        transactions = self.get_all_league_transactions(league_id)
        # Filter for trades
        trade_transactions = [t for t in transactions if t['type'] == 'trade']
        
        formatted_trades = []
        for trade in trade_transactions:
            trade_info = {
                'date': datetime.fromtimestamp(trade['created'] / 1000).strftime('%Y-%m-%d %I:%M %p'),
                'received': [],
                'given': []
            }

            # Get roster mapping once per trade
            rosters = self.client.league_manager.get_league_rosters(league_id)
            roster_id_to_team = {}
            for roster in rosters:
                users = self.client.league_manager.get_league_users(league_id)
                team = next((team for team in users if team.user_id == roster.owner_id), None)
                if team:
                    roster_id_to_team[roster.roster_id] = team.display_name

            # Process adds (received players)
            if trade['adds']:
                for player_id, roster_id in trade['adds'].items():
                    trade_info['received'].append({
                        'player': self.client.player_manager.get_player_name(player_id),
                        'team': roster_id_to_team.get(roster_id, f"Team {roster_id}")
                    })

            # Process drops (given players)
            if trade['drops']:
                for player_id, roster_id in trade['drops'].items():
                    trade_info['given'].append({
                        'player': self.client.player_manager.get_player_name(player_id),
                        'team': roster_id_to_team.get(roster_id, f"Team {roster_id}")
                    })

            formatted_trades.append(trade_info)

        return formatted_trades 