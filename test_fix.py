#!/usr/bin/env python3
"""Test if the fix works."""

import sys
sys.path.append('src')
from client import SleeperAPI
import json

def test_fix():
    client = SleeperAPI()
    league_id = "1181025001438806016"
    
    # Re-process trades to see if the fix works
    trades = client.transaction_service.get_trades(league_id)
    
    print("=== Testing the fix ===\n")
    
    # Find the problematic trade
    for trade in trades:
        if trade.get('date') == '2023-04-07 11:22 AM':
            print(f"Found the trade from {trade['date']}")
            
            if 'team_assets' in trade:
                for team, assets in trade['team_assets'].items():
                    for asset in assets.get('receives', []) + assets.get('gives', []):
                        if (asset.get('type') == 'draft_pick' and 
                            asset.get('season') == '2025' and 
                            asset.get('round') == 1 and
                            asset.get('original_owner') == 'emanueljd3'):
                            
                            print(f"\nTeam: {team}")
                            print(f"Original owner: {asset.get('original_owner')}")
                            print(f"Pick number: {asset.get('pick_number')}")
                            print(f"Player: {asset.get('player_name')}")
                            
                            if asset.get('pick_number') == 10:
                                print("✓ FIXED! Pick number is now correctly 10")
                            else:
                                print("✗ Still broken - pick number is not 10")
            break
    
    # Also check other picks to make sure we didn't break anything
    print("\n=== Checking other 2025 first round picks ===")
    
    for trade in trades[:10]:  # Check first 10 trades
        if 'team_assets' in trade:
            for team, assets in trade['team_assets'].items():
                for asset in assets.get('receives', []):
                    if (asset.get('type') == 'draft_pick' and 
                        asset.get('season') == '2025' and 
                        asset.get('round') == 1 and
                        asset.get('pick_number')):
                        
                        print(f"\n{asset.get('original_owner')}'s pick:")
                        print(f"  Pick #{asset.get('pick_number')} - {asset.get('player_name')}")

if __name__ == "__main__":
    test_fix()