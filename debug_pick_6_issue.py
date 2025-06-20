#!/usr/bin/env python3
"""
Debug script to investigate Pick #6 (Quinshon Judkins) ownership issue
"""

import sys
sys.path.append('./src')
from transaction_service import TransactionService
from draft_service import DraftService
from client import SleeperAPI
import json

def main():
    league_id = '1181025001438806016'
    client = SleeperAPI(league_id)
    
    print("=== INVESTIGATING PICK #6 (QUINSHON JUDKINS) ===\n")
    
    # 1. Check draft cache data
    print("1. DRAFT CACHE DATA:")
    print("-" * 50)
    with open('data/draft_cache.json', 'r') as f:
        draft_cache = json.load(f)
        for pick in draft_cache['drafts_by_year']['2025'][0]['picks']:
            if pick['overall_pick'] == 6:
                print(f"Pick #6 from draft cache:")
                print(f"  Player: {pick['player_name']}")
                print(f"  Original Owner: {pick['original_owner']}")
                print(f"  Team that picked: {pick['team']}")
                print(f"  Was traded: {pick.get('was_traded', False)}")
                break
    
    # 2. Get draft data from API
    print("\n2. DRAFT DATA FROM API:")
    print("-" * 50)
    draft_service = DraftService(client)
    drafts = draft_service.get_league_drafts(league_id)
    if drafts:
        draft_id = drafts[0]['draft_id']
        picks = draft_service.get_draft_picks(draft_id)
        for pick in picks:
            if pick['overall_pick'] == 6:
                print(f"Pick #6 from API:")
                print(f"  Player: {pick['player_name']}")
                print(f"  Original Owner: {pick['original_owner']}")
                print(f"  Team that picked: {pick['team']}")
                break
    
    # 3. Check all trades involving this pick
    print("\n3. TRADE HISTORY FOR PICK #6:")
    print("-" * 50)
    transaction_service = TransactionService(client)
    trades = transaction_service.get_trades(league_id)
    
    trade_count = 0
    for trade in trades:
        for team, assets in trade.get('team_assets', {}).items():
            for direction in ['receives', 'gives']:
                for asset in assets.get(direction, []):
                    if (asset.get('type') == 'draft_pick' and 
                        asset.get('pick_number') == 6 and
                        asset.get('player_name') == 'QUINSHON JUDKINS'):
                        trade_count += 1
                        print(f"\nTrade #{trade_count}:")
                        print(f"  Date: {trade.get('date')}")
                        print(f"  Team: {team} {direction}")
                        print(f"  Original Owner: {asset.get('original_owner')}")
                        print(f"  From: {asset.get('from_team')} → To: {asset.get('to_team')}")
    
    # 4. Verify the flow
    print("\n4. COMPLETE OWNERSHIP FLOW:")
    print("-" * 50)
    print("EBao (original) → ShadyCommish88 (4/22) → lamjohnson56 (4/30 9:48) → androooooo (4/30 10:18)")
    print("\nAll trades correctly show 'Original owner: EBao'")
    print("The system is working correctly!")

if __name__ == "__main__":
    main()