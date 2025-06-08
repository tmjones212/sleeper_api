#!/usr/bin/env python3
"""Analyze the raw transaction data to understand the issue."""

import sys
sys.path.append('src')
from client import SleeperAPI
import json

def analyze_raw_transaction():
    client = SleeperAPI()
    
    # We need to check the 2023 league since that's when the trade happened
    league_2023 = "916445745966915584"
    
    print("=== Checking 2023 league transactions ===")
    
    # Get transactions from 2023
    all_trans_2023 = client.transaction_service.get_all_league_transactions(league_2023)
    
    # Find the April 7, 2023 trade
    for trans in all_trans_2023:
        if (trans.get('created_datetime') == '2023-04-07 11:22 AM' and 
            trans['type'] == 'trade'):
            print(f"\nFound transaction in 2023 league!")
            print(f"Transaction ID: {trans.get('transaction_id')}")
            print(f"Roster IDs involved: {trans.get('roster_ids')}")
            
            if trans.get('draft_picks'):
                print("\nDraft picks:")
                for pick in trans['draft_picks']:
                    if pick['season'] == '2025':
                        print(json.dumps(pick, indent=2))
                        
                        # Now trace what happens when this gets processed
                        print(f"\nProcessing this pick...")
                        
                        # Get roster mapping for 2023
                        rosters_2023 = client.league_service.get_league_rosters(league_2023)
                        users_2023 = client.league_service.get_league_users(league_2023)
                        roster_to_team_2023 = {}
                        for roster in rosters_2023:
                            team = next((u for u in users_2023 if u.user_id == roster.owner_id), None)
                            if team:
                                roster_to_team_2023[roster.roster_id] = team.display_name
                        
                        print(f"Roster {pick.get('roster_id')} in 2023 = {roster_to_team_2023.get(pick.get('roster_id'))}")
                        print(f"Previous owner {pick.get('previous_owner_id')} = {roster_to_team_2023.get(pick.get('previous_owner_id'))}")
                        
                        # Test what _get_draft_pick_details returns
                        result = client.transaction_service._get_draft_pick_details(
                            pick, roster_to_team_2023, league_2023
                        )
                        print(f"\n_get_draft_pick_details result:")
                        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    analyze_raw_transaction()