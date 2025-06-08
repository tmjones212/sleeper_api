#!/usr/bin/env python3
"""Trace the exact issue with emanueljd3's pick assignment."""

import sys
sys.path.append('src')
from client import SleeperAPI
import json

def trace_pick_issue():
    client = SleeperAPI()
    league_id = "1181025001438806016"
    
    # First, let's understand the draft order
    print("=== 2025 Draft Order ===")
    from draft_service import DraftService
    draft_service = DraftService(client)
    
    drafts = draft_service.get_league_drafts(league_id)
    if drafts:
        draft_order = drafts[0].get('processed_draft_order', {})
        print("Draft positions:")
        for position in sorted(draft_order.keys()):
            print(f"  Position {position}: {draft_order[position]}")
    
    # Now let's look at a specific problematic transaction
    print("\n=== Analyzing problematic transaction ===")
    
    # Get roster mapping
    rosters = client.league_service.get_league_rosters(league_id)
    users = client.league_service.get_league_users(league_id)
    roster_to_team = {}
    for roster in rosters:
        team = next((u for u in users if u.user_id == roster.owner_id), None)
        if team:
            roster_to_team[roster.roster_id] = team.display_name
    
    # Simulate what happens when processing emanueljd3's pick
    # Based on the trade from 2023-04-07
    pick_data = {
        'season': '2025',
        'round': 1,
        'roster_id': 7,  # This should be emanueljd3's roster
        'previous_owner_id': 7,
        'owner_id': 1  # Traded to someone else
    }
    
    print(f"\nProcessing pick with roster_id={pick_data['roster_id']}")
    print(f"Roster {pick_data['roster_id']} belongs to: {roster_to_team.get(pick_data['roster_id'])}")
    
    # Test the _get_draft_pick_details function
    result = client.transaction_service._get_draft_pick_details(
        pick_data, roster_to_team, league_id
    )
    
    print(f"\nResult from _get_draft_pick_details:")
    print(json.dumps(result, indent=2))
    
    # Now check what the draft position is for emanueljd3
    print("\n=== Draft position analysis ===")
    for pos, team in draft_order.items():
        if team == 'emanueljd3':
            print(f"emanueljd3 has draft position: {pos}")
            print(f"In a 12-team league, position {pos} gets pick #{pos} in round 1")

if __name__ == "__main__":
    trace_pick_issue()