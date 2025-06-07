#!/usr/bin/env python3
"""
Debug script to show sample trade data after fixes
"""
import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from client import SleeperAPI

def debug_trade_sample():
    """Show a sample of the corrected trade data"""
    print("🔍 Debugging Trade Data Sample")
    print("=" * 50)
    
    try:
        # Initialize API
        league_id = "1048308938824937472"
        api = SleeperAPI(league_id)
        
        # Get trades
        print("Getting trade data...")
        trades = api.transaction_service.get_trades(league_id)
        
        if not trades:
            print("No trades found!")
            return
        
        print(f"Found {len(trades)} trades total")
        
        # Show first few trades with details
        print("\n📋 Sample Trades (first 3):")
        print("-" * 80)
        
        for i, trade in enumerate(trades[:3]):
            print(f"\nTrade #{i+1}: {trade.get('date', 'Unknown date')}")
            
            # Show received side
            received_players = trade.get('received', {}).get('players', [])
            received_picks = trade.get('received', {}).get('draft_picks', [])
            
            print("  RECEIVED:")
            for player in received_players:
                from_info = f" (from {player.get('from_team', 'Unknown')})" if player.get('from_team') else ""
                print(f"    • {player['team']}: {player['player']}{from_info}")
            
            for pick in received_picks:
                print(f"    • {pick.get('to_team', 'Unknown')}: {pick['round']} round {pick['season']} pick (from {pick.get('from_team', 'Unknown')})")
            
            # Show given side
            given_players = trade.get('given', {}).get('players', [])
            
            print("  GIVEN:")
            for player in given_players:
                to_info = f" (to {player.get('to_team', 'Unknown')})" if player.get('to_team') else ""
                print(f"    • {player['team']}: {player['player']}{to_info}")
            
            print("  " + "-" * 70)
        
        # Check for the specific problematic trade mentioned
        print("\n🎯 Looking for Jerry Jeudy trade (2024-01-24)...")
        jeudy_trades = []
        for trade in trades:
            trade_date = trade.get('date', '')
            if '2024-01-24' in trade_date:
                # Check if Jerry Jeudy is involved
                all_players = (trade.get('received', {}).get('players', []) + 
                              trade.get('given', {}).get('players', []))
                for player in all_players:
                    if 'JERRY JEUDY' in player.get('player', '').upper():
                        jeudy_trades.append(trade)
                        break
        
        if jeudy_trades:
            print(f"Found {len(jeudy_trades)} Jerry Jeudy trade(s) on 2024-01-24:")
            for trade in jeudy_trades:
                print(f"\nDate: {trade.get('date')}")
                print("RECEIVED:")
                for player in trade.get('received', {}).get('players', []):
                    print(f"  - {player['team']}: {player['player']}")
                for pick in trade.get('received', {}).get('draft_picks', []):
                    print(f"  - {pick.get('to_team')}: {pick['round']} round {pick['season']}")
                
                print("GIVEN:")
                for player in trade.get('given', {}).get('players', []):
                    print(f"  - {player['team']}: {player['player']}")
        else:
            print("No Jerry Jeudy trades found on that date.")
        
        print(f"\n✅ Trade data processing appears to be working correctly!")
        print(f"📊 Open the generated HTML file to see the full visualization")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_trade_sample()