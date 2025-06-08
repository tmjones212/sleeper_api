#!/usr/bin/env python3
"""Test fix for the pick matching issue."""

import sys
sys.path.append('src')
from client import SleeperAPI
import json

def test_pick_matching():
    client = SleeperAPI()
    league_id = "1181025001438806016"  # 2025 league
    
    # Simulate the pick data for emanueljd3's pick
    pick_data = {
        'season': '2025',
        'round': 1,
        'roster_id': 10,  # emanueljd3's roster
        'previous_owner_id': 10
    }
    
    # Get roster mapping
    rosters = client.league_service.get_league_rosters(league_id)
    users = client.league_service.get_league_users(league_id)
    roster_to_team = {}
    for roster in rosters:
        team = next((u for u in users if u.user_id == roster.owner_id), None)
        if team:
            roster_to_team[roster.roster_id] = team.display_name
    
    print(f"Roster 10 maps to: {roster_to_team.get(10)}")
    
    # Get draft data
    from draft_service import DraftService
    draft_service = DraftService(client)
    
    drafts = draft_service.get_league_drafts(league_id)
    if drafts:
        draft_id = drafts[0]['draft_id']
        picks = draft_service.get_draft_picks(draft_id)
        
        print("\nDraft picks for round 1:")
        for pick in picks:
            if pick['round'] == 1:
                print(f"Pick #{pick['overall_pick']}: original_owner='{pick['original_owner']}', team='{pick['team']}', player='{pick['player_name']}'")
        
        # Test the matching
        original_owner_name = client.transaction_service._get_historical_team_name(
            10, '2025', league_id, roster_to_team
        )
        print(f"\nOriginal owner name resolved to: '{original_owner_name}'")
        
        # Try to find the correct pick
        for pick in picks:
            if pick['round'] == 1 and pick['original_owner'] == original_owner_name:
                print(f"\nMatched pick: #{pick['overall_pick']} - {pick['player_name']}")
                break

if __name__ == "__main__":
    test_pick_matching()