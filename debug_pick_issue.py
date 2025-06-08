#!/usr/bin/env python3
"""Debug the pick number issue for emanueljd3's 2025 first round pick."""

import sys
sys.path.append('src')
from client import SleeperAPI
import json

def debug_pick_issue():
    client = SleeperAPI()
    league_id = "1181025001438806016"  # 2025 league
    
    # Get all transactions
    transactions = client.transaction_service.get_all_league_transactions(league_id)
    
    # Find trades involving emanueljd3's 2025 first round pick
    for trans in transactions:
        if trans['type'] == 'trade' and trans.get('draft_picks'):
            for pick in trans['draft_picks']:
                if (pick['season'] == '2025' and 
                    pick['round'] == 1):
                    
                    print(f"\nFound trade with emanueljd3's 2025 1st round pick:")
                    print(f"Transaction ID: {trans.get('transaction_id')}")
                    print(f"Date: {trans.get('created_datetime')}")
                    print(f"Pick data: {json.dumps(pick, indent=2)}")
                    
                    # Get the roster mapping
                    rosters = client.league_service.get_league_rosters(league_id)
                    users = client.league_service.get_league_users(league_id)
                    roster_to_team = {}
                    for roster in rosters:
                        team = next((u for u in users if u.user_id == roster.owner_id), None)
                        if team:
                            roster_to_team[roster.roster_id] = team.display_name
                    
                    print(f"\nRoster to team mapping:")
                    for rid, tname in sorted(roster_to_team.items()):
                        print(f"  Roster {rid}: {tname}")
                    
                    # Test the _get_draft_pick_details function
                    draft_details = client.transaction_service._get_draft_pick_details(
                        pick, roster_to_team, league_id
                    )
                    print(f"\nDraft details returned: {json.dumps(draft_details, indent=2)}")
                    
                    # Check the draft cache directly
                    with open('data/draft_cache.json', 'r') as f:
                        draft_cache = json.load(f)
                    
                    if '2025' in draft_cache['drafts_by_year']:
                        picks_2025 = draft_cache['drafts_by_year']['2025'][0]['picks']
                        # Find emanueljd3's pick
                        for dpick in picks_2025:
                            if dpick['original_owner'] == 'emanueljd3' and dpick['round'] == 1:
                                print(f"\nFound in draft cache:")
                                print(f"  Pick number: {dpick['overall_pick']}")
                                print(f"  Original owner: {dpick['original_owner']}")
                                print(f"  Current team: {dpick['team']}")
                                print(f"  Player: {dpick['player_name']}")

if __name__ == "__main__":
    debug_pick_issue()