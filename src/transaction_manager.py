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
        filename = os.path.join('data', f'league_{league_id}_transactions.json')
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(all_transactions, f, indent=2)
        
        return all_transactions

    def get_trades(self, league_id: str) -> List[Dict[str, Any]]:
        """Get all trades for a league, including historical trades."""
        all_transactions = self.get_all_historical_transactions(league_id)
        
        # Get roster mapping
        rosters = self.client.league_manager.get_league_rosters(league_id)
        users = self.client.league_manager.get_league_users(league_id)
        roster_to_team = {}
        for roster in rosters:
            team = next((u for u in users if u.user_id == roster.owner_id), None)
            if team:
                roster_to_team[roster.roster_id] = team.display_name
        
        # Filter for trade transactions and enhance them
        trades = []
        for transaction in all_transactions:
            if transaction['type'] == 'trade':
                trade_info = {
                    'date': datetime.fromtimestamp(transaction['created'] / 1000).strftime('%Y-%m-%d %I:%M %p'),
                    'league_id': league_id,
                    'received': {
                        'players': [],
                        'draft_picks': []
                    },
                    'given': {
                        'players': [],
                        'draft_picks': []
                    }
                }
                
                # Process players
                if transaction.get('adds'):
                    for player_id, roster_id in transaction['adds'].items():
                        trade_info['received']['players'].append({
                            'player': self.client.player_manager.get_player_name(player_id),
                            'team': roster_to_team.get(roster_id, f"Team {roster_id}")
                        })
                
                if transaction.get('drops'):
                    for player_id, roster_id in transaction['drops'].items():
                        trade_info['given']['players'].append({
                            'player': self.client.player_manager.get_player_name(player_id),
                            'team': roster_to_team.get(roster_id, f"Team {roster_id}")
                        })
                
                # Process draft picks
                if transaction.get('draft_picks'):
                    for pick in transaction['draft_picks']:
                        # For each pick, determine if it's being received or given based on owner_id
                        pick_info = {
                            'round': pick['round'],
                            'season': pick['season'],
                            'from_team': roster_to_team.get(pick['previous_owner_id'], f"Team {pick['previous_owner_id']}"),
                            'to_team': roster_to_team.get(pick['owner_id'], f"Team {pick['owner_id']}")
                        }
                        trade_info['received']['draft_picks'].append(pick_info)
                
                trades.append(trade_info)
        
        return trades

    def get_trades_by_manager(self, league_id: str, manager_name: str) -> List[Dict[str, Any]]:
        """
        Get all trades involving a specific manager (case insensitive).
        Shows both players and draft picks received/given in trades.
        """
        # Get primary team name and aliases
        primary_team_name = self.client.team_manager.get_primary_name(manager_name)
        if not primary_team_name:
            return []
        
        # Get all trades
        all_trades = self.get_all_league_transactions(league_id)
        trade_transactions = [t for t in all_trades if t['type'] == 'trade']
        
        # Get roster mapping
        rosters = self.client.league_manager.get_league_rosters(league_id)
        users = self.client.league_manager.get_league_users(league_id)
        roster_to_team = {}
        for roster in rosters:
            team = next((u for u in users if u.user_id == roster.owner_id), None)
            if team:
                roster_to_team[roster.roster_id] = team.display_name

        # Get manager's roster IDs (they might have multiple)
        manager_roster_ids = {
            roster.roster_id 
            for roster in rosters 
            for user in users 
            if user.user_id == roster.owner_id 
            and self.client.team_manager.is_same_team(user.display_name, manager_name)
        }

        manager_trades = []
        for trade in trade_transactions:
            # Skip if manager not involved
            if not any(rid in manager_roster_ids for rid in trade['roster_ids']):
                continue

            trade_info = {
                'date': datetime.fromtimestamp(trade['created'] / 1000).strftime('%Y-%m-%d %I:%M %p'),
                'received': {
                    'players': [],
                    'draft_picks': []
                },
                'given': {
                    'players': [],
                    'draft_picks': []
                }
            }

            # Process players
            if trade.get('adds'):
                for player_id, roster_id in trade['adds'].items():
                    is_receiving = roster_id in manager_roster_ids
                    category = 'received' if is_receiving else 'given'
                    trade_info[category]['players'].append({
                        'player': self.client.player_manager.get_player_name(player_id),
                        'team': roster_to_team.get(roster_id, f"Team {roster_id}")
                    })

            # Process draft picks
            if trade.get('draft_picks'):
                for pick in trade['draft_picks']:
                    is_receiving = pick['owner_id'] in manager_roster_ids
                    category = 'received' if is_receiving else 'given'
                    trade_info[category]['draft_picks'].append({
                        'round': pick['round'],
                        'season': pick['season'],
                        'from_team': roster_to_team.get(pick['previous_owner_id'], f"Team {pick['previous_owner_id']}"),
                        'to_team': roster_to_team.get(pick['owner_id'], f"Team {pick['owner_id']}")
                    })

            manager_trades.append(trade_info)

        return manager_trades

    def get_trades_by_player(self, league_id: str, player_name: str) -> List[Dict[str, Any]]:
        """Get all trades involving a specific player (case insensitive)."""
        player_name = player_name.lower()
        all_trades = self.get_trades(league_id)
        
        player_trades = []
        for trade in all_trades:
            # Check if player is involved in either receiving or giving
            player_involved = any(move['player'].lower() == player_name for move in trade['received'])
            player_involved |= any(move['player'].lower() == player_name for move in trade['given'])
            
            if player_involved:
                player_trades.append(trade)
        
        return player_trades

    def get_all_historical_transactions(self, league_id: str) -> List[Dict[str, Any]]:
        """Get all transactions from the current league and all previous leagues."""
        all_transactions = []
        current_league = self.client.league_manager.get_league(league_id)
        
        # Process current league
        all_transactions.extend(self.get_all_league_transactions(league_id))
        
        # Follow the previous_league_id chain
        while hasattr(current_league, 'previous_league_id') and current_league.previous_league_id:
            previous_league_id = current_league.previous_league_id
            all_transactions.extend(self.get_all_league_transactions(previous_league_id))
            current_league = self.client.league_manager.get_league(previous_league_id)
        
        return all_transactions 