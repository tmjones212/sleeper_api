#!/usr/bin/env python3
"""Debug emanueljd3's pick specifically."""

import sys
sys.path.append('src')
from client import SleeperAPI
import json

def debug_emanueljd3_pick():
    client = SleeperAPI()
    league_id = "1181025001438806016"  # 2025 league
    
    # Get all trades
    trades = client.transaction_service.get_trades(league_id)
    
    print("=== Searching for trades involving emanueljd3's 2025 1st round pick ===\n")
    
    found_count = 0
    for i, trade in enumerate(trades):
        if 'team_assets' in trade:
            for team_name, assets in trade['team_assets'].items():
                # Check receives
                for asset in assets.get('receives', []):
                    if (asset.get('type') == 'draft_pick' and 
                        asset.get('season') == '2025' and 
                        asset.get('round') == 1 and
                        'emanueljd3' in str(asset.get('original_owner', '')).lower()):
                        found_count += 1
                        print(f"FOUND #{found_count} - Trade #{i+1}, Date: {trade.get('date')}")
                        print(f"Team {team_name} RECEIVES:")
                        print(json.dumps(asset, indent=2))
                        print()
                
                # Check gives
                for asset in assets.get('gives', []):
                    if (asset.get('type') == 'draft_pick' and 
                        asset.get('season') == '2025' and 
                        asset.get('round') == 1 and
                        'emanueljd3' in str(asset.get('original_owner', '')).lower()):
                        found_count += 1
                        print(f"FOUND #{found_count} - Trade #{i+1}, Date: {trade.get('date')}")
                        print(f"Team {team_name} GIVES:")
                        print(json.dumps(asset, indent=2))
                        print()
    
    print(f"\nTotal trades found involving emanueljd3's 2025 1st: {found_count}")
    
    # Also check for any pick with pick_number = 1 that shouldn't be
    print("\n=== Checking for incorrect pick_number = 1 assignments ===\n")
    
    for i, trade in enumerate(trades):
        if 'team_assets' in trade:
            for team_name, assets in trade['team_assets'].items():
                for asset in assets.get('receives', []) + assets.get('gives', []):
                    if (asset.get('type') == 'draft_pick' and 
                        asset.get('pick_number') == 1 and
                        asset.get('season') == '2025'):
                        print(f"Trade #{i+1}: {team_name} has pick_number=1")
                        print(f"Original owner: {asset.get('original_owner')}")
                        print(f"Player: {asset.get('player_name')}")
                        if asset.get('original_owner') != 'caviar89':
                            print("*** WARNING: This should not be pick #1! ***")
                        print()

if __name__ == "__main__":
    debug_emanueljd3_pick()