#!/usr/bin/env python3
"""Debug the draft order to understand the roster ID mapping."""

import sys
sys.path.append('src')
from client import SleeperAPI
import json

def debug_draft_order():
    client = SleeperAPI()
    
    # Check the 2025 draft
    league_2025 = "1181025001438806016"
    
    from draft_service import DraftService
    draft_service = DraftService(client)
    
    drafts = draft_service.get_league_drafts(league_2025)
    if drafts:
        print("=== 2025 Draft Information ===")
        print(f"Draft ID: {drafts[0]['draft_id']}")
        
        # Check draft_order
        draft_order = drafts[0].get('draft_order', {})
        print("\nDraft order (raw):")
        print(json.dumps(draft_order, indent=2))
        
        # Check slot_to_roster_id
        slot_to_roster = drafts[0].get('slot_to_roster_id', {})
        print("\nSlot to roster mapping:")
        for slot, roster_id in sorted(slot_to_roster.items(), key=lambda x: int(x[0])):
            print(f"  Slot {slot} -> Roster ID {roster_id}")
        
        # Get the processed draft order
        processed_order = drafts[0].get('processed_draft_order', {})
        print("\nProcessed draft order:")
        for pos in sorted(processed_order.keys()):
            print(f"  Position {pos}: {processed_order[pos]}")
        
        # Now check which roster ID emanueljd3 has in 2025
        rosters = client.league_service.get_league_rosters(league_2025)
        users = client.league_service.get_league_users(league_2025)
        
        print("\n2025 League roster mapping:")
        for roster in sorted(rosters, key=lambda x: x.roster_id):
            user = next((u for u in users if u.user_id == roster.owner_id), None)
            if user:
                if user.display_name == 'emanueljd3':
                    print(f"  *** Roster {roster.roster_id}: {user.display_name} ***")
                else:
                    print(f"  Roster {roster.roster_id}: {user.display_name}")

if __name__ == "__main__":
    debug_draft_order()