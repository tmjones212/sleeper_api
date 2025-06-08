#!/usr/bin/env python3
"""Find the trade where emanueljd3's pick gets assigned #1."""

import sys
sys.path.append('src')
from client import SleeperAPI
import json

def find_problematic_trade():
    client = SleeperAPI()
    league_id = "1181025001438806016"
    
    # Get processed trades (not raw transactions)
    trades = client.transaction_service.get_trades(league_id)
    
    print("=== Finding trades with emanueljd3's 2025 1st assigned as pick #1 ===\n")
    
    problematic_trades = []
    
    for i, trade in enumerate(trades):
        if 'team_assets' in trade:
            has_problem = False
            trade_details = {
                'index': i,
                'date': trade.get('date'),
                'teams': []
            }
            
            for team_name, assets in trade['team_assets'].items():
                for direction in ['receives', 'gives']:
                    for asset in assets.get(direction, []):
                        if (asset.get('type') == 'draft_pick' and 
                            asset.get('season') == '2025' and 
                            asset.get('round') == 1 and
                            asset.get('original_owner') == 'emanueljd3' and
                            asset.get('pick_number') == 1):
                            has_problem = True
                            trade_details['teams'].append({
                                'team': team_name,
                                'direction': direction,
                                'asset': asset
                            })
            
            if has_problem:
                problematic_trades.append(trade_details)
                print(f"Trade #{i} - {trade.get('date')}")
                print(f"Teams involved: {[t['team'] for t in trade_details['teams']]}")
                for team_detail in trade_details['teams']:
                    print(f"\n{team_detail['team']} {team_detail['direction'].upper()}:")
                    print(f"  Pick #1 (should be #10!)")
                    print(f"  Original owner: emanueljd3")
                    print(f"  Player: {team_detail['asset'].get('player_name')}")
                print("\n" + "-"*50 + "\n")
    
    print(f"\nTotal problematic trades found: {len(problematic_trades)}")
    
    # Now let's check what the raw transaction data looks like
    if problematic_trades:
        first_problem = problematic_trades[0]
        print(f"\n=== Checking raw transaction for trade from {first_problem['date']} ===")
        
        # Get historical transactions
        all_trans = client.transaction_service.get_all_historical_transactions(league_id)
        
        # Find matching transaction by date
        for trans in all_trans:
            if (trans.get('type') == 'trade' and 
                trans.get('created_datetime') and 
                first_problem['date'] in trans.get('created_datetime')):
                
                print(f"\nFound transaction {trans.get('transaction_id')}")
                if trans.get('draft_picks'):
                    for pick in trans['draft_picks']:
                        if pick['season'] == '2025' and pick['round'] == 1:
                            print(f"\nRaw pick data:")
                            print(json.dumps(pick, indent=2))

if __name__ == "__main__":
    find_problematic_trade()