#!/usr/bin/env python3
"""Test the matching logic to understand the bug."""

import sys
sys.path.append('src')
from client import SleeperAPI
import json

def test_matching_logic():
    client = SleeperAPI()
    
    # We're processing a trade from 2023 league but need to match to 2025 draft
    league_2023 = "916445745966915584"
    league_2025 = "1181025001438806016"
    
    # Simulate the pick data from the 2023 trade
    pick_data = {
        "round": 1,
        "season": "2025",
        "league_id": None,
        "roster_id": 7,  # emanueljd3's roster in 2023
        "owner_id": 3,   # EBao's roster in 2023
        "previous_owner_id": 7
    }
    
    # Get 2023 roster mapping
    rosters_2023 = client.league_service.get_league_rosters(league_2023)
    users_2023 = client.league_service.get_league_users(league_2023)
    roster_to_team_2023 = {}
    for roster in rosters_2023:
        team = next((u for u in users_2023 if u.user_id == roster.owner_id), None)
        if team:
            roster_to_team_2023[roster.roster_id] = team.display_name
    
    print("=== Testing the matching process ===\n")
    
    # Step 1: Get historical team name
    original_owner_name = client.transaction_service._get_historical_team_name(
        pick_data['roster_id'], pick_data['season'], league_2023, roster_to_team_2023
    )
    print(f"Step 1 - Historical team name for roster {pick_data['roster_id']}: {original_owner_name}")
    
    # Step 2: Find the 2025 league
    target_league_id = client.transaction_service._find_league_for_season(league_2023, '2025')
    print(f"Step 2 - Target league for 2025: {target_league_id}")
    
    # Step 3: Get draft picks from 2025
    from draft_service import DraftService
    draft_service = DraftService(client)
    
    drafts = draft_service.get_league_drafts(target_league_id)
    if drafts:
        draft_id = drafts[0]['draft_id']
        picks = draft_service.get_draft_picks(draft_id)
        
        print(f"\nStep 3 - Checking draft {draft_id}")
        print("Round 1 picks:")
        for pick in picks:
            if pick['round'] == 1:
                match = "*** MATCH ***" if pick['original_owner'] == original_owner_name else ""
                print(f"  Pick #{pick['overall_pick']}: original_owner='{pick['original_owner']}' {match}")
        
        # Step 4: Try the matching strategies
        print(f"\nStep 4 - Matching strategies for original_owner_name='{original_owner_name}'")
        
        # Strategy 1: Direct name match
        print("\nStrategy 1 - Direct name match:")
        for pick in picks:
            if pick['round'] == 1 and pick['original_owner'] == original_owner_name:
                print(f"  MATCHED: Pick #{pick['overall_pick']} - {pick['player_name']}")
                break
        else:
            print("  No match found")
        
        # Check if there's a name mismatch issue
        print("\nDebugging: All unique original owners in draft:")
        unique_owners = set(pick['original_owner'] for pick in picks if pick['round'] == 1)
        for owner in sorted(unique_owners):
            print(f"  '{owner}'")
        
        # Check for case sensitivity or whitespace issues
        print("\nChecking for near matches:")
        for pick in picks:
            if pick['round'] == 1:
                if original_owner_name.lower() in pick['original_owner'].lower():
                    print(f"  Partial match: '{pick['original_owner']}' contains '{original_owner_name}'")

if __name__ == "__main__":
    test_matching_logic()