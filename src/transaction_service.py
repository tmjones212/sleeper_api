from datetime import datetime
import os
import json
from typing import List, Dict, Any

class TransactionService:
    def __init__(self, client):
        self.client = client

    def get_all_league_transactions(self, league_id: str) -> List[Dict[str, Any]]:
        """
        Get all transactions for a league, starting from week 1 until no more transactions are found.
        Enhances transactions with team name information.
        """
        # Get league data to map roster_ids to team names
        league = self.client.league_service.get_league(league_id, fetch_all=True)
        team_names = {team.roster.roster_id: team.display_name for team in league.teams if team.roster}
        
        all_transactions = []
        week = 1
        
        while True:
            transactions = self.client.league_service.get_league_transactions(league_id, week)
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
        rosters = self.client.league_service.get_league_rosters(league_id)
        users = self.client.league_service.get_league_users(league_id)
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
                
                # Process players correctly - each player appears in BOTH adds and drops with different roster_ids
                # adds[player_id] = destination_roster_id (where player is going)
                # drops[player_id] = source_roster_id (where player came from)
                
                # Group assets by team to build proper trade sides
                team_assets = {}
                all_roster_ids = set(transaction.get('roster_ids', []))
                
                # Initialize team assets structure
                for roster_id in all_roster_ids:
                    team_name = roster_to_team.get(roster_id, f"Team {roster_id}")
                    team_assets[team_name] = {'receives': [], 'gives': []}
                
                # Process players - each player moves from one team to another
                if transaction.get('adds') and transaction.get('drops'):
                    for player_id in transaction['adds']:
                        if player_id in transaction['drops']:
                            player_name = self.client.player_service.get_player_name(player_id)
                            
                            # Where player is going (destination)
                            receiving_roster_id = transaction['adds'][player_id]
                            receiving_team = roster_to_team.get(receiving_roster_id, f"Team {receiving_roster_id}")
                            
                            # Where player came from (source)  
                            giving_roster_id = transaction['drops'][player_id]
                            giving_team = roster_to_team.get(giving_roster_id, f"Team {giving_roster_id}")
                            
                            # Add to receiving team's assets
                            if receiving_team in team_assets:
                                team_assets[receiving_team]['receives'].append({
                                    'player': player_name,
                                    'from_team': giving_team
                                })
                            
                            # Add to giving team's assets  
                            if giving_team in team_assets:
                                team_assets[giving_team]['gives'].append({
                                    'player': player_name,
                                    'to_team': receiving_team
                                })
                
                # Use the correct team_assets structure instead of the broken received/given format
                trade_info['team_assets'] = team_assets
                
                # Keep the old format for backward compatibility but fix it
                for team_name, assets in team_assets.items():
                    # Only add what this team RECEIVES to the received list
                    for asset in assets['receives']:
                        trade_info['received']['players'].append({
                            'player': asset['player'],
                            'team': team_name,
                            'from_team': asset.get('from_team')
                        })
                    
                    # Only add what this team GIVES to the given list  
                    for asset in assets['gives']:
                        trade_info['given']['players'].append({
                            'player': asset['player'], 
                            'team': team_name,
                            'to_team': asset.get('to_team')
                        })
                
                # Process draft picks
                if transaction.get('draft_picks'):
                    for pick in transaction['draft_picks']:
                        pick_info = {
                            'round': pick['round'],
                            'season': pick['season'],
                            'from_team': roster_to_team.get(pick['previous_owner_id'], f"Team {pick['previous_owner_id']}"),
                            'to_team': roster_to_team.get(pick['owner_id'], f"Team {pick['owner_id']}")
                        }
                        
                        # Add to receiving team (current owner)
                        receiving_team = roster_to_team.get(pick['owner_id'], f"Team {pick['owner_id']}")
                        if receiving_team in team_assets:
                            team_assets[receiving_team]['receives'].append({
                                'type': 'draft_pick',
                                'round': pick['round'],
                                'season': pick['season'],
                                'from_team': pick_info['from_team']
                            })
                        
                        # Add to giving team (previous owner)
                        giving_team = roster_to_team.get(pick['previous_owner_id'], f"Team {pick['previous_owner_id']}")
                        if giving_team in team_assets:
                            team_assets[giving_team]['gives'].append({
                                'type': 'draft_pick',
                                'round': pick['round'],
                                'season': pick['season'],
                                'to_team': pick_info['to_team']
                            })
                        
                        # Also add to the main structure for backward compatibility
                        trade_info['received']['draft_picks'].append(pick_info)
                
                # Process FAAB (waiver budget) trades
                if transaction.get('waiver_budget'):
                    for faab_transfer in transaction['waiver_budget']:
                        amount = faab_transfer.get('amount', 0)
                        receiver_roster_id = faab_transfer.get('receiver')
                        sender_roster_id = faab_transfer.get('sender')
                        
                        if amount > 0 and receiver_roster_id and sender_roster_id:
                            receiving_team = roster_to_team.get(receiver_roster_id, f"Team {receiver_roster_id}")
                            giving_team = roster_to_team.get(sender_roster_id, f"Team {sender_roster_id}")
                            
                            # Add to receiving team's assets
                            if receiving_team in team_assets:
                                team_assets[receiving_team]['receives'].append({
                                    'type': 'faab',
                                    'amount': amount,
                                    'from_team': giving_team
                                })
                            
                            # Add to giving team's assets
                            if giving_team in team_assets:
                                team_assets[giving_team]['gives'].append({
                                    'type': 'faab',
                                    'amount': amount,
                                    'to_team': receiving_team
                                })
                
                trades.append(trade_info)
        
        return trades

    def get_trades_by_manager(self, league_id: str, manager_name: str) -> List[Dict[str, Any]]:
        """
        Get all trades involving a specific manager (case insensitive).
        Shows both players and draft picks received/given in trades.
        """
        # Get primary team name and aliases
        primary_team_name = self.client.team_service.get_primary_name(manager_name)
        if not primary_team_name:
            return []
        
        # Get all trades
        all_trades = self.get_all_league_transactions(league_id)
        trade_transactions = [t for t in all_trades if t['type'] == 'trade']
        
        # Get roster mapping
        rosters = self.client.league_service.get_league_rosters(league_id)
        users = self.client.league_service.get_league_users(league_id)
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
            and self.client.team_service.is_same_team(user.display_name, manager_name)
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

            # Process players - each player appears in both adds and drops with different roster_ids
            # adds[player_id] = destination_roster_id (where player is going)
            # drops[player_id] = source_roster_id (where player came from)
            if trade.get('adds') and trade.get('drops'):
                for player_id in trade['adds']:
                    if player_id in trade['drops']:
                        destination_roster = trade['adds'][player_id]
                        source_roster = trade['drops'][player_id]
                        
                        # If manager is receiving this player
                        if destination_roster in manager_roster_ids:
                            trade_info['received']['players'].append({
                                'player': self.client.player_service.get_player_name(player_id),
                                'from_team': roster_to_team.get(source_roster, f"Team {source_roster}")
                            })
                        
                        # If manager is giving this player
                        elif source_roster in manager_roster_ids:
                            trade_info['given']['players'].append({
                                'player': self.client.player_service.get_player_name(player_id),
                                'to_team': roster_to_team.get(destination_roster, f"Team {destination_roster}")
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
        current_league = self.client.league_service.get_league(league_id)
        
        # Process current league
        all_transactions.extend(self.get_all_league_transactions(league_id))
        
        # Follow the previous_league_id chain
        while hasattr(current_league, 'previous_league_id') and current_league.previous_league_id:
            previous_league_id = current_league.previous_league_id
            all_transactions.extend(self.get_all_league_transactions(previous_league_id))
            current_league = self.client.league_service.get_league(previous_league_id)
        
        return all_transactions

    def get_player_trade_counts(self, league_id: str) -> Dict[str, int]:
        """
        Get a count of how many times each player has been traded in the league's history.
        Returns a dictionary mapping player names to their trade count.
        Each trade is counted only once per player, regardless of whether they were received or given.
        """
        all_trades = self.get_trades(league_id)
        player_trade_counts = {}
        
        for trade in all_trades:
            # Get unique players involved in this trade
            players_in_trade = set()
            
            # Add players from both received and given
            for move in trade['received']['players']:
                players_in_trade.add(move['player'])
            for move in trade['given']['players']:
                players_in_trade.add(move['player'])
            
            # Count each player only once per trade
            for player_name in players_in_trade:
                player_trade_counts[player_name] = player_trade_counts.get(player_name, 0) + 1
        
        # Sort by trade count in descending order
        sorted_counts = dict(sorted(player_trade_counts.items(), key=lambda x: x[1], reverse=True))
        return sorted_counts

    def get_player_trade_history(self, league_id: str, player_name: str) -> List[Dict[str, Any]]:
        """
        Get detailed trade history for a specific player.
        Returns a list of trades with full details including:
        - Date of trade
        - Teams involved and what they received
        Trades are sorted by date in descending order (most recent first).
        """
        all_trades = self.get_trades(league_id)
        player_trades = []
        
        for trade in all_trades:
            # Check if player is involved in this trade
            players_in_trade = set()
            for move in trade['received']['players']:
                players_in_trade.add(move['player'])
            for move in trade['given']['players']:
                players_in_trade.add(move['player'])
            
            if player_name in players_in_trade:
                player_trades.append(trade)
        
        # Sort trades by date in descending order
        player_trades.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d %I:%M %p'), reverse=True)
        
        return player_trades

    def get_manager_trade_history(self, league_id: str, manager_name: str) -> List[Dict[str, Any]]:
        """
        Get all trades made by a specific manager.
        Returns a list of trades with full details including:
        - Date of trade
        - Teams involved and what they received
        Trades are sorted by date in descending order (most recent first).
        """
        all_trades = self.get_trades(league_id)
        manager_trades = []
        
        for trade in all_trades:
            # Check if manager is involved in this trade
            teams_in_trade = set()
            
            # Check received players
            for move in trade['received']['players']:
                teams_in_trade.add(move['team'])
            
            # Check given players
            for move in trade['given']['players']:
                teams_in_trade.add(move['team'])
            
            if manager_name in teams_in_trade:
                manager_trades.append(trade)
        
        # Sort trades by date in descending order
        manager_trades.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d %I:%M %p'), reverse=True)
        
        return manager_trades 