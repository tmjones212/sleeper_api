#!/usr/bin/env python3

import sys
sys.path.append('src')

import json
from client import SleeperAPI
from transaction_service import TransactionService

def main():
    # Initialize client
    client = SleeperAPI()
    transaction_service = TransactionService(client)
    
    # Get trades
    league_id = '1181025001438806016'
    trades = transaction_service.get_trades(league_id)
    
    # Find the specific trade with duplicates (2024-11-01 08:40 AM)
    target_trade = None
    for trade in trades:
        if trade['date'] == '2024-11-01 08:40 AM':
            target_trade = trade
            break
    
    if not target_trade:
        print("Target trade not found")
        return
    
    print("Found target trade:")
    print(f"Date: {target_trade['date']}")
    print(f"Teams involved: {list(target_trade['team_assets'].keys())}")
    
    # Check for duplicate picks in team_assets
    all_picks = []
    for team_name, assets in target_trade['team_assets'].items():
        print(f"\n{team_name}:")
        print(f"  Receives: {len(assets['receives'])} items")
        for item in assets['receives']:
            if item.get('type') == 'draft_pick':
                pick_key = f"R{item['round']}-{item['season']}-{item.get('pick_number', '?')}-{item.get('player_name', '?')}"
                all_picks.append(pick_key)
                print(f"    RECEIVES: {pick_key}")
        
        print(f"  Gives: {len(assets['gives'])} items")
        for item in assets['gives']:
            if item.get('type') == 'draft_pick':
                pick_key = f"R{item['round']}-{item['season']}-{item.get('pick_number', '?')}-{item.get('player_name', '?')}"
                all_picks.append(pick_key)
                print(f"    GIVES: {pick_key}")
    
    # Count duplicates
    print(f"\nTotal picks found: {len(all_picks)}")
    pick_counts = {}
    for pick in all_picks:
        pick_counts[pick] = pick_counts.get(pick, 0) + 1
    
    duplicates = {k: v for k, v in pick_counts.items() if v > 1}
    if duplicates:
        print(f"DUPLICATES FOUND: {duplicates}")
    else:
        print("No duplicates in team_assets structure")

if __name__ == "__main__":
    main()