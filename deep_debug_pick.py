#!/usr/bin/env python3
"""Deep debug of the pick assignment issue."""

import sys
sys.path.append('src')
from client import SleeperAPI
import json

def deep_debug_pick():
    client = SleeperAPI()
    
    # Let's trace through exactly what happens
    print("=== Deep debugging the pick assignment ===\n")
    
    # Simulate processing a historical trade with emanueljd3's pick
    league_id = "916445745966915584"  # 2023 league
    target_league_id = "1181025001438806016"  # 2025 league
    
    # This is the pick data from the 2023 trade
    pick_data = {
        "round": 1,
        "season": "2025",
        "roster_id": 7,
        "owner_id": 3,
        "previous_owner_id": 7
    }
    
    # Get roster mapping for 2023
    rosters = client.league_service.get_league_rosters(league_id)
    users = client.league_service.get_league_users(league_id)
    roster_to_team = {}
    for roster in rosters:
        team = next((u for u in users if u.user_id == roster.owner_id), None)
        if team:
            roster_to_team[roster.roster_id] = team.display_name
    
    print(f"In 2023 league, roster {pick_data['roster_id']} = {roster_to_team.get(7)}")
    
    # Now let's manually trace through _get_draft_pick_details
    print("\n=== Tracing _get_draft_pick_details ===")
    
    # Step 1: Get source team name
    source_team_name = client.transaction_service._get_historical_team_name(
        pick_data['roster_id'], pick_data['season'], league_id, roster_to_team
    )
    print(f"Step 1: source_team_name = '{source_team_name}'")
    
    # Step 2: Get draft data
    from draft_service import DraftService
    draft_service = DraftService(client)
    
    drafts = draft_service.get_league_drafts(target_league_id)
    draft_id = drafts[0]['draft_id']
    picks = draft_service.get_draft_picks(draft_id)
    
    # Step 3: Check what the code is doing
    draft_order_raw = drafts[0].get('draft_order', {})
    target_users = client.league_service.get_league_users(target_league_id)
    
    name_to_user_id = {}
    for user in target_users:
        name_to_user_id[user.display_name] = user.user_id
    
    user_id_in_target = name_to_user_id.get(source_team_name)
    print(f"Step 2: user_id for '{source_team_name}' = {user_id_in_target}")
    
    if user_id_in_target and user_id_in_target in draft_order_raw:
        draft_position = draft_order_raw[user_id_in_target]
        print(f"Step 3: draft_position = {draft_position}")
    
    # Step 4: Check the matching
    print(f"\n=== Checking pick matching for '{source_team_name}' ===")
    
    for pick in picks:
        if pick['round'] == 1 and pick['original_owner'] == source_team_name:
            print(f"MATCH FOUND: Pick #{pick['overall_pick']} - {pick['player_name']}")
            print(f"  original_owner: '{pick['original_owner']}'")
            print(f"  This is the pick that gets returned")
            break
    else:
        print("NO MATCH FOUND")
        
        # Debug why no match
        print("\nAll round 1 original owners:")
        for pick in picks:
            if pick['round'] == 1:
                print(f"  Pick #{pick['overall_pick']}: '{pick['original_owner']}'")
        
        print(f"\nLooking for: '{source_team_name}'")
        
        # Check if it's a case sensitivity issue
        for pick in picks:
            if pick['round'] == 1:
                if source_team_name.lower() == pick['original_owner'].lower():
                    print(f"  Case mismatch: '{source_team_name}' vs '{pick['original_owner']}'")

if __name__ == "__main__":
    deep_debug_pick()