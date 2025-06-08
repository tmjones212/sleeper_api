#!/usr/bin/env python3
"""Debug the actual transaction data."""

import sys
sys.path.append('src')
from client import SleeperAPI
import json

def debug_transaction_data():
    client = SleeperAPI()
    league_id = "1181025001438806016"
    
    # Get all transactions
    all_trans = client.transaction_service.get_all_league_transactions(league_id)
    
    print("=== Looking for the problematic transaction (2023-04-07 11:22 AM) ===\n")
    
    for trans in all_trans:
        if (trans.get('created_datetime') == '2023-04-07 11:22 AM' and 
            trans['type'] == 'trade'):
            print(f"Found transaction {trans.get('transaction_id')}")
            
            if trans.get('draft_picks'):
                print("\nDraft picks in this transaction:")
                for i, pick in enumerate(trans['draft_picks']):
                    if pick['season'] == '2025' and pick['round'] == 1:
                        print(f"\nPick #{i+1}:")
                        print(json.dumps(pick, indent=2))
                        
                        # Check who this pick originally belonged to
                        roster_id = pick.get('roster_id')
                        print(f"\nAnalyzing roster_id {roster_id}:")
                        
                        # Get roster mapping
                        rosters = client.league_service.get_league_rosters(league_id)
                        users = client.league_service.get_league_users(league_id)
                        
                        for roster in rosters:
                            if roster.roster_id == roster_id:
                                user = next((u for u in users if u.user_id == roster.owner_id), None)
                                if user:
                                    print(f"  Current owner of roster {roster_id}: {user.display_name}")
                                break
            
            print("\n" + "="*50 + "\n")
            
            # Now let's see what happens when this gets processed into trades
            trades = client.transaction_service.get_trades(league_id)
            
            # Find this specific trade in the processed trades
            for trade in trades:
                if trade.get('date') == '2023-04-07 11:22 AM':
                    print("Found corresponding processed trade!")
                    if 'team_assets' in trade:
                        for team, assets in trade['team_assets'].items():
                            for asset in assets.get('receives', []) + assets.get('gives', []):
                                if (asset.get('type') == 'draft_pick' and 
                                    asset.get('season') == '2025' and 
                                    asset.get('round') == 1):
                                    print(f"\nTeam {team}:")
                                    print(json.dumps(asset, indent=2))

if __name__ == "__main__":
    debug_transaction_data()