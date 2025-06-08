#!/usr/bin/env python3
"""Regenerate trade data to apply the fix."""

import sys
import os
sys.path.append('src')
from client import SleeperAPI

def regenerate_trade_data():
    print("=== Regenerating trade visualization ===")
    
    client = SleeperAPI()
    league_id = "1181025001438806016"
    
    # Clear any cached transaction data
    cache_file = f"data/league_{league_id}_transactions.json"
    if os.path.exists(cache_file):
        print(f"Removing cached transactions: {cache_file}")
        os.remove(cache_file)
    
    # Force re-fetch of all transactions
    print("Fetching fresh transaction data...")
    client.transaction_service.get_all_league_transactions(league_id)
    
    # Generate the visualization
    from trade_visualization_service import LeagueVisualizationService
    viz_service = LeagueVisualizationService(client)
    
    output_file = f"trade_visualization_league_{league_id}_fixed.html"
    print(f"Generating visualization to: {output_file}")
    
    viz_service.save_league_visualization(league_id, output_file)
    
    print(f"\n✓ Visualization saved to: {output_file}")
    print("Open this file to see if emanueljd3's pick is now correctly shown as #10")
    
    # Also let's specifically check the problematic trade
    trades = client.transaction_service.get_trades(league_id)
    
    print("\n=== Checking emanueljd3's 2025 1st round pick ===")
    found = False
    for trade in trades:
        if 'team_assets' in trade:
            for team, assets in trade['team_assets'].items():
                for asset in assets.get('receives', []) + assets.get('gives', []):
                    if (asset.get('type') == 'draft_pick' and 
                        asset.get('season') == '2025' and 
                        asset.get('round') == 1 and
                        asset.get('original_owner') == 'emanueljd3'):
                        
                        if not found:
                            found = True
                            print(f"\nFound emanueljd3's 2025 1st:")
                            print(f"  Pick number: #{asset.get('pick_number')}")
                            print(f"  Player: {asset.get('player_name')}")
                            if asset.get('pick_number') == 10:
                                print("  ✓ CORRECT!")
                            else:
                                print("  ✗ Still incorrect")

if __name__ == "__main__":
    regenerate_trade_data()