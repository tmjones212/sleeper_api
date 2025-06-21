from datetime import datetime
import os
import json
from typing import List, Dict, Any, Optional

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
            elif roster.roster_id == 9 and league_id == "1048308938824937472":
                # Special case: Roster 9 belongs to caviar89 but has owner_id=None
                caviar_user = next((u for u in users if u.user_id == "1176293990462615552"), None)
                if caviar_user:
                    roster_to_team[roster.roster_id] = caviar_user.display_name
        
        # Filter for trade transactions and enhance them
        trades = []
        for transaction in all_transactions:
            if transaction['type'] == 'trade':
                trade_info = {
                    'date': datetime.fromtimestamp(transaction['status_updated'] / 1000).strftime('%Y-%m-%d %I:%M %p'),
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
                                    'player_id': player_id,
                                    'from_team': giving_team
                                })
                            
                            # Add to giving team's assets  
                            if giving_team in team_assets:
                                team_assets[giving_team]['gives'].append({
                                    'player': player_name,
                                    'player_id': player_id,
                                    'to_team': receiving_team
                                })
                
                # Use the correct team_assets structure instead of the broken received/given format
                trade_info['team_assets'] = team_assets
                
                # Keep the old format for backward compatibility but fix it
                for team_name, assets in team_assets.items():
                    # Only add what this team RECEIVES to the received list
                    for asset in assets['receives']:
                        if 'player' in asset:  # Only add player assets
                            trade_info['received']['players'].append({
                                'player': asset['player'],
                                'player_id': asset.get('player_id'),
                                'team': team_name,
                                'from_team': asset.get('from_team')
                            })
                    
                    # Only add what this team GIVES to the given list  
                    for asset in assets['gives']:
                        if 'player' in asset:  # Only add player assets
                            trade_info['given']['players'].append({
                                'player': asset['player'],
                                'player_id': asset.get('player_id'), 
                                'team': team_name,
                                'to_team': asset.get('to_team')
                            })
                
                # Process draft picks
                if transaction.get('draft_picks'):
                    for pick in transaction['draft_picks']:
                        # Get improved team name mapping that handles historical seasons
                        from_team = self._get_historical_team_name(pick['previous_owner_id'], pick['season'], league_id, roster_to_team)
                        to_team = self._get_historical_team_name(pick['owner_id'], pick['season'], league_id, roster_to_team)
                        
                        # Get the original owner using roster_id (original draft slot) instead of previous_owner_id
                        original_roster_id = pick.get('roster_id', pick['previous_owner_id'])
                        original_owner = self._get_historical_team_name(original_roster_id, pick['season'], league_id, roster_to_team)
                        
                        pick_info = {
                            'round': pick['round'],
                            'season': pick['season'],
                            'from_team': from_team,
                            'to_team': to_team
                        }
                        
                        # Try to get actual draft pick details if draft has happened
                        draft_details = self._get_draft_pick_details(pick, roster_to_team, league_id)
                        if draft_details:
                            pick_info.update(draft_details)
                        
                        # Create the pick asset once
                        pick_asset = {
                            'type': 'draft_pick',
                            'round': pick['round'],
                            'season': pick['season'],
                            'original_owner': original_owner,
                            'from_team': from_team,
                            'to_team': to_team
                        }
                        # Add draft details if available
                        if draft_details:
                            pick_asset.update(draft_details)
                        
                        # Add to receiving team's receives list (with deduplication)
                        receiving_team = to_team
                        if receiving_team in team_assets:
                            # Check if this exact pick asset already exists
                            pick_exists = any(
                                existing_pick.get('type') == 'draft_pick' and
                                existing_pick.get('round') == pick_asset['round'] and
                                existing_pick.get('season') == pick_asset['season'] and
                                existing_pick.get('original_owner') == pick_asset.get('original_owner') and
                                existing_pick.get('player_name') == pick_asset.get('player_name')
                                for existing_pick in team_assets[receiving_team]['receives']
                            )
                            if not pick_exists:
                                team_assets[receiving_team]['receives'].append(pick_asset.copy())
                        
                        # Add to giving team's gives list (with deduplication)
                        giving_team = from_team
                        if giving_team in team_assets:
                            # Check if this exact pick asset already exists
                            pick_exists = any(
                                existing_pick.get('type') == 'draft_pick' and
                                existing_pick.get('round') == pick_asset['round'] and
                                existing_pick.get('season') == pick_asset['season'] and
                                existing_pick.get('original_owner') == pick_asset.get('original_owner') and
                                existing_pick.get('player_name') == pick_asset.get('player_name')
                                for existing_pick in team_assets[giving_team]['gives']
                            )
                            if not pick_exists:
                                team_assets[giving_team]['gives'].append(pick_asset.copy())
                        
                
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
                
                # Add timestamp for sorting
                trade_info['timestamp'] = transaction['status_updated']
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
            elif roster.roster_id == 9 and league_id == "1048308938824937472":
                # Special case: Roster 9 belongs to caviar89 but has owner_id=None
                caviar_user = next((u for u in users if u.user_id == "1176293990462615552"), None)
                if caviar_user:
                    roster_to_team[roster.roster_id] = caviar_user.display_name

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
                'date': datetime.fromtimestamp(trade['status_updated'] / 1000).strftime('%Y-%m-%d %I:%M %p'),
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
                    
                    # Get the original owner using roster_id (original draft slot) instead of previous_owner_id
                    original_roster_id = pick.get('roster_id', pick['previous_owner_id'])
                    original_owner = self._get_historical_team_name(original_roster_id, pick['season'], league_id, roster_to_team)
                    
                    pick_info = {
                        'round': pick['round'],
                        'season': pick['season'],
                        'original_owner': original_owner,
                        'from_team': roster_to_team.get(pick['previous_owner_id'], f"Team {pick['previous_owner_id']}"),
                        'to_team': roster_to_team.get(pick['owner_id'], f"Team {pick['owner_id']}")
                    }
                    
                    # Try to get actual draft pick details if draft has happened
                    draft_details = self._get_draft_pick_details(pick, roster_to_team, league_id)
                    if draft_details:
                        pick_info.update(draft_details)
                    
                    trade_info[category]['draft_picks'].append(pick_info)

            # Add timestamp for sorting
            trade_info['timestamp'] = trade['status_updated']
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
    
    def _get_draft_pick_details(self, pick_data: Dict[str, Any], roster_to_team: Dict[int, str], league_id: str) -> Optional[Dict[str, Any]]:
        """Get actual draft pick details (pick number, player) if the draft has happened."""
        try:
            season = pick_data['season']
            round_num = pick_data['round']
            
            # Try to find the league for this season by following the league chain
            target_league_id = self._find_league_for_season(league_id, season)
            if not target_league_id:
                return None
            
            # Get draft data for that season
            from draft_service import DraftService
            draft_service = DraftService(self.client)
            
            try:
                drafts = draft_service.get_league_drafts(target_league_id)
                if not drafts:
                    return None
                
                # Get the main draft (usually first one)
                draft_id = drafts[0]['draft_id']
                picks = draft_service.get_draft_picks(draft_id)
                
                # Get better team name for original owner (use roster_id, not previous_owner_id)
                # roster_id represents the original draft slot, previous_owner_id is just who traded it
                original_roster_id = pick_data.get('roster_id', pick_data['previous_owner_id'])
                
                # For cross-league trades, we need to map the roster ID from the source league
                # to the correct team in the target league where the draft happens
                
                # First, get the team name in the source league
                source_team_name = self._get_historical_team_name(
                    original_roster_id, pick_data.get('season', season), league_id, roster_to_team
                )
                
                # Now find this team in the target league's draft order
                draft_order_raw = drafts[0].get('draft_order', {})
                target_users = self.client.league_service.get_league_users(target_league_id)
                
                # Create a mapping of user display names to user IDs in the target league
                name_to_user_id = {}
                for user in target_users:
                    name_to_user_id[user.display_name] = user.user_id
                
                # Find the user ID for the source team name
                user_id_in_target = name_to_user_id.get(source_team_name)
                
                # Use the team name from the target league
                original_owner_name = source_team_name
                
                # Double-check by looking at draft position if we have the user ID
                if user_id_in_target and user_id_in_target in draft_order_raw:
                    draft_position = draft_order_raw[user_id_in_target]
                    # Verify this matches what we expect
                    processed_order = drafts[0].get('processed_draft_order', {})
                    if str(draft_position) in processed_order:
                        original_owner_name = processed_order[str(draft_position)]
                
                # Try multiple matching strategies
                for draft_pick in picks:
                    # Strategy 1: Match by round and original owner name
                    if (draft_pick['round'] == round_num and 
                        draft_pick['original_owner'] == original_owner_name):
                        return {
                            'pick_number': draft_pick['overall_pick'],
                            'player_name': draft_pick['player_name'],
                            'player_id': draft_pick['player_id'],
                            'position': draft_pick['position'],
                            'image_url': draft_pick.get('image_url'),
                            'picking_team': draft_pick.get('team')  # Who actually made the pick
                        }
                
                # Strategy 2: Match by round and pick number if we can calculate it
                if 'roster_id' in pick_data:
                    # Try to find pick by calculated position
                    draft_order = drafts[0].get('processed_draft_order', {})
                    for position, team_name in draft_order.items():
                        if team_name == original_owner_name:
                            # Calculate the pick number for this round and position
                            teams_count = len(draft_order)
                            position_int = int(position)  # Convert position to int
                            if round_num % 2 == 1:  # Odd rounds go 1,2,3...
                                pick_in_round = position_int
                            else:  # Even rounds go ...3,2,1
                                pick_in_round = teams_count - position_int + 1
                            
                            overall_pick = ((round_num - 1) * teams_count) + pick_in_round
                            
                            # Find the pick with this overall pick number
                            for draft_pick in picks:
                                if draft_pick['overall_pick'] == overall_pick:
                                    return {
                                        'pick_number': draft_pick['overall_pick'],
                                        'player_name': draft_pick['player_name'],
                                        'player_id': draft_pick['player_id'],
                                        'position': draft_pick['position'],
                                        'image_url': draft_pick.get('image_url'),
                                        'picking_team': draft_pick.get('team')  # Who actually made the pick
                                    }
                            break
                            
            except Exception as e:
                print(f"Could not get draft details for {season} round {round_num}: {e}")
                return None
                
        except Exception as e:
            print(f"Error getting draft pick details: {e}")
            return None
        
        return None

    def _find_league_for_season(self, league_id: str, season: int) -> Optional[str]:
        """Find the league ID for a specific season by following the league chain."""
        try:
            current_league = self.client.league_service.get_league(league_id)
            
            # Check current league season
            if str(current_league.season) == str(season):
                return league_id
            
            # Follow previous_league_id chain to find the right season
            while hasattr(current_league, 'previous_league_id') and current_league.previous_league_id:
                previous_league_id = current_league.previous_league_id
                current_league = self.client.league_service.get_league(previous_league_id)
                if str(current_league.season) == str(season):
                    return previous_league_id
            
            return None
        except Exception as e:
            print(f"Error finding league for season {season}: {e}")
            return None

    def _get_historical_team_name(self, roster_id: int, season: int, league_id: str, current_roster_to_team: Dict[int, str]) -> str:
        """Get team name for a roster ID, handling historical seasons properly."""
        try:
            # Handle known team transitions for this specific league
            if league_id == '1181025001438806016':
                # Handle the caviar89 transition - they took over from a previous team
                # If roster_id 9 and before caviar89 joined, use a better fallback name
                if roster_id == 9 and int(season) < 2025:
                    # Try to find the actual historical name, but use a better fallback
                    season_league_id = self._find_league_for_season(league_id, season)
                    if season_league_id:
                        try:
                            season_rosters = self.client.league_service.get_league_rosters(season_league_id)
                            season_users = self.client.league_service.get_league_users(season_league_id)
                            
                            for roster in season_rosters:
                                if roster.roster_id == roster_id:
                                    user = next((u for u in season_users if u.user_id == roster.owner_id), None)
                                    if user:
                                        return user.display_name
                                    break
                        except Exception:
                            pass
                    # Better fallback for the previous team owner
                    return f"Previous Team {roster_id}"
            
            # First try current mapping
            if roster_id in current_roster_to_team:
                team_name = current_roster_to_team[roster_id]
                # If it's not a generic "Team X" name, use it
                if not team_name.startswith("Team "):
                    return team_name
            
            # Try to find the specific league for this season
            season_league_id = self._find_league_for_season(league_id, season)
            if season_league_id:
                try:
                    # Get the rosters and users for that specific season
                    season_rosters = self.client.league_service.get_league_rosters(season_league_id)
                    season_users = self.client.league_service.get_league_users(season_league_id)
                    
                    # Create season-specific mapping
                    for roster in season_rosters:
                        if roster.roster_id == roster_id:
                            user = next((u for u in season_users if u.user_id == roster.owner_id), None)
                            if user:
                                return user.display_name
                            break
                except Exception as e:
                    print(f"Error getting historical team name for roster {roster_id} in season {season}: {e}")
            
            # Fallback to current mapping or generic name
            return current_roster_to_team.get(roster_id, f"Team {roster_id}")
            
        except Exception as e:
            print(f"Error in _get_historical_team_name: {e}")
            return current_roster_to_team.get(roster_id, f"Team {roster_id}")

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