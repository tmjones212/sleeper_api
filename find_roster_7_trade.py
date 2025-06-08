#!/usr/bin/env python3
"""Find the specific trade with roster 7's 2025 first."""

import sys
sys.path.append('src')
from client import SleeperAPI
import json

def find_roster_7_trade():
    client = SleeperAPI()
    
    # Load the 2023 transactions
    with open('data/league_916445745966915584_transactions.json', 'r') as f:
        transactions = json.load(f)
    
    print("=== Finding trades with roster_id 7's 2025 first round pick ===\n")
    
    # Get roster mapping for 2023
    league_2023 = "916445745966915584"
    rosters_2023 = client.league_service.get_league_rosters(league_2023)
    users_2023 = client.league_service.get_league_users(league_2023)
    roster_to_team_2023 = {}
    roster_to_user_id = {}
    
    for roster in rosters_2023:
        team = next((u for u in users_2023 if u.user_id == roster.owner_id), None)
        if team:
            roster_to_team_2023[roster.roster_id] = team.display_name
            roster_to_user_id[roster.roster_id] = roster.owner_id
    
    print("2023 Roster mapping:")
    for rid in sorted(roster_to_team_2023.keys()):
        print(f"  Roster {rid} = {roster_to_team_2023[rid]} (user_id: {roster_to_user_id.get(rid)})")
    
    print("\n=== Trades involving roster 7's 2025 1st ===\n")
    
    for trans in transactions:
        if trans['type'] == 'trade' and trans.get('draft_picks'):
            for pick in trans['draft_picks']:
                if (pick['season'] == '2025' and 
                    pick['round'] == 1 and 
                    pick['roster_id'] == 7):
                    
                    print(f"Transaction ID: {trans['transaction_id']}")
                    print(f"Date: {trans.get('created_datetime')}")
                    print(f"Status: {trans.get('status')}")
                    
                    # Show the pick movement
                    prev_owner = roster_to_team_2023.get(pick['previous_owner_id'], f"User {pick['previous_owner_id']}")
                    new_owner = roster_to_team_2023.get(pick['owner_id'], f"User {pick['owner_id']}")
                    
                    print(f"Pick movement: {prev_owner} -> {new_owner}")
                    print(f"Raw pick data: {json.dumps(pick, indent=2)}")
                    
                    # Now test what happens when this is processed
                    print("\nTesting _get_draft_pick_details...")
                    result = client.transaction_service._get_draft_pick_details(
                        pick, roster_to_team_2023, league_2023
                    )
                    if result:
                        print(f"Result: Pick #{result.get('pick_number')} - {result.get('player_name')}")
                    else:
                        print("Result: None (draft not found)")
                    
                    print("\n" + "-"*50 + "\n")

if __name__ == "__main__":
    find_roster_7_trade()