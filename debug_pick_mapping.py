#!/usr/bin/env python3
"""Debug the pick number mapping issue."""

import sys
sys.path.append('src')
from client import SleeperAPI
import json

def debug_pick_mapping():
    client = SleeperAPI()
    league_id = "1181025001438806016"  # 2025 league
    
    # Load draft cache
    with open('data/draft_cache.json', 'r') as f:
        draft_cache = json.load(f)
    
    print("=== 2025 Draft Pick Mapping ===")
    print("\nFirst round picks:")
    if '2025' in draft_cache['drafts_by_year']:
        picks = draft_cache['drafts_by_year']['2025'][0]['picks']
        for pick in picks:
            if pick['round'] == 1:
                print(f"Pick #{pick['overall_pick']}: {pick['original_owner']} -> {pick['team']} ({pick['player_name']})")
    
    # Now check a specific trade to see how pick_number is assigned
    print("\n=== Checking Trade Processing ===")
    
    # Get trades
    trades = client.transaction_service.get_trades(league_id)
    
    # Find trades with draft picks
    for trade in trades[:5]:  # Check first 5 trades
        if 'team_assets' in trade:
            for team_name, assets in trade['team_assets'].items():
                for asset in assets.get('receives', []):
                    if (asset.get('type') == 'draft_pick' and 
                        asset.get('season') == '2025' and 
                        asset.get('round') == 1):
                        print(f"\nTeam: {team_name}")
                        print(f"Receives: {json.dumps(asset, indent=2)}")
                        
                        # Check if emanueljd3 is involved
                        if 'emanueljd3' in str(asset.get('original_owner', '')).lower():
                            print("*** This is emanueljd3's pick! ***")
                            if asset.get('pick_number'):
                                print(f"*** Assigned pick number: {asset.get('pick_number')} ***")

if __name__ == "__main__":
    debug_pick_mapping()