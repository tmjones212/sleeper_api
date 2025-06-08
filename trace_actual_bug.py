#!/usr/bin/env python3
"""Trace the actual bug in the pick assignment."""

import sys
sys.path.append('src')
from client import SleeperAPI
import json

def trace_actual_bug():
    client = SleeperAPI()
    
    # Start from the 2025 league where we see the issue
    league_2025 = "1181025001438806016"
    
    print("=== Tracing the bug from 2025 league perspective ===\n")
    
    # Get trades from the 2025 league that show the issue
    trades = client.transaction_service.get_trades(league_2025)
    
    # Find the problematic trade
    for i, trade in enumerate(trades):
        if trade.get('date') == '2023-04-07 11:22 AM':
            print(f"Found the problematic trade #{i}")
            print(f"Date: {trade['date']}")
            
            # Look at the team_assets
            if 'team_assets' in trade:
                for team, assets in trade['team_assets'].items():
                    for asset in assets.get('receives', []) + assets.get('gives', []):
                        if (asset.get('type') == 'draft_pick' and 
                            asset.get('season') == '2025' and 
                            asset.get('round') == 1 and
                            asset.get('original_owner') == 'emanueljd3'):
                            
                            print(f"\nTeam: {team}")
                            print(f"Asset: {json.dumps(asset, indent=2)}")
                            
                            # The bug is here - pick_number is 1 but should be 10
                            print(f"\nBUG: pick_number = {asset.get('pick_number')} (should be 10)")
                            print(f"Player assigned: {asset.get('player_name')} (TRAVIS HUNTER)")
                            print(f"But TRAVIS HUNTER is actually pick #1 (caviar89's pick)")
            
            # Now let's trace where this comes from
            print("\n=== Tracing the source ===")
            
            # Get the raw transaction that created this trade
            all_historical = client.transaction_service.get_all_historical_transactions(league_2025)
            
            for trans in all_historical:
                if (trans.get('created_datetime') == '2023-04-07 11:22 AM' and 
                    trans['type'] == 'trade'):
                    print(f"\nFound source transaction: {trans['transaction_id']}")
                    print(f"From league: {trans.get('league_id', 'unknown')}")
                    
                    if trans.get('draft_picks'):
                        for pick in trans['draft_picks']:
                            if pick['season'] == '2025' and pick['round'] == 1:
                                print(f"\nRaw pick data:")
                                print(json.dumps(pick, indent=2))
                                
                                # This is where we need to understand the matching
                                print("\nThe issue is likely in _get_draft_pick_details")
                                print("It's matching by player name instead of original owner")
                                print("TRAVIS HUNTER was drafted #1 by whoever got caviar89's pick")
                                print("But the code is incorrectly assigning him to emanueljd3's pick")
            
            break

if __name__ == "__main__":
    trace_actual_bug()