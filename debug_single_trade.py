#!/usr/bin/env python3
"""
Debug a single trade to understand the data structure
"""
import sys
import os
import json

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from client import SleeperAPI

def debug_single_trade():
    """Debug a single trade to understand what's happening"""
    print("🔍 Debugging Single Trade")
    print("=" * 50)
    
    try:
        # Load raw transaction data first
        with open('data/league_1048308938824937472_transactions.json', 'r') as f:
            raw_transactions = json.load(f)
        
        # Find a trade transaction
        trade_transactions = [t for t in raw_transactions if t.get('type') == 'trade']
        
        if not trade_transactions:
            print("No trade transactions found")
            return
        
        # Look at the first trade
        raw_trade = trade_transactions[0]
        print("📋 RAW TRANSACTION DATA:")
        print(f"Transaction ID: {raw_trade.get('transaction_id')}")
        print(f"Date: {raw_trade.get('created')}")
        print(f"Status: {raw_trade.get('status')}")
        print(f"Type: {raw_trade.get('type')}")
        print(f"Roster IDs: {raw_trade.get('roster_ids', [])}")
        print(f"Adds: {raw_trade.get('adds', {})}")
        print(f"Drops: {raw_trade.get('drops', {})}")
        print(f"Draft picks: {raw_trade.get('draft_picks', [])}")
        print()
        
        # Initialize API and process the trade
        api = SleeperAPI("1048308938824937472")
        
        # Get processed trades
        trades = api.transaction_service.get_trades("1048308938824937472")
        
        # Find the corresponding processed trade by checking transaction details
        processed_trade = None
        for trade in trades:
            # Try to match by date or other criteria
            if raw_trade.get('created'):
                from datetime import datetime
                raw_date = datetime.fromtimestamp(raw_trade['created'] / 1000).strftime('%Y-%m-%d %I:%M %p')
                if trade.get('date') == raw_date:
                    processed_trade = trade
                    break
        
        if not processed_trade:
            processed_trade = trades[0]  # Use first trade as example
        
        print("🔧 PROCESSED TRADE DATA:")
        print(f"Date: {processed_trade.get('date')}")
        print("\nRECEIVED players:")
        for player in processed_trade.get('received', {}).get('players', []):
            print(f"  - {player['team']}: {player['player']} (from {player.get('from_team', 'Unknown')})")
        
        print("\nGIVEN players:")
        for player in processed_trade.get('given', {}).get('players', []):
            print(f"  - {player['team']}: {player['player']} (to {player.get('to_team', 'Unknown')})")
        
        print("\nRECEIVED draft picks:")
        for pick in processed_trade.get('received', {}).get('draft_picks', []):
            print(f"  - {pick.get('to_team')}: {pick['round']} round {pick['season']} (from {pick.get('from_team')})")
        
        # Analysis
        received_player_names = set(p['player'] for p in processed_trade.get('received', {}).get('players', []))
        given_player_names = set(p['player'] for p in processed_trade.get('given', {}).get('players', []))
        overlap = received_player_names.intersection(given_player_names)
        
        print(f"\n🔍 ANALYSIS:")
        print(f"Received player names: {received_player_names}")
        print(f"Given player names: {given_player_names}")
        print(f"Overlap (identical): {overlap}")
        
        if overlap:
            print("❌ PROBLEM: Same players appear on both sides!")
            print("\nThis means the trade processing is wrong.")
            
            # Let's trace through what should happen
            print("\n🧮 WHAT SHOULD HAPPEN:")
            adds = raw_trade.get('adds', {})
            drops = raw_trade.get('drops', {})
            
            for player_id in adds:
                if player_id in drops:
                    from_roster = drops[player_id]
                    to_roster = adds[player_id]
                    player_name = api.player_service.get_player_name(player_id)
                    print(f"Player {player_name} should move FROM roster {from_roster} TO roster {to_roster}")
        else:
            print("✅ GOOD: No overlap - different players on each side")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_single_trade()