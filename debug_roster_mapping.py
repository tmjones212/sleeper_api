#!/usr/bin/env python3
"""Debug the roster ID mapping issue."""

import sys
sys.path.append('src')
from client import SleeperAPI
import json

def debug_roster_mapping():
    client = SleeperAPI()
    
    # The problematic pick data from a 2023 trade
    pick_data = {
        "round": 1,
        "season": "2025",
        "roster_id": 7,  # emanueljd3's roster in 2023
        "owner_id": 3,
        "previous_owner_id": 7
    }
    
    print("=== Debugging roster mapping ===")
    print(f"Pick data: roster_id={pick_data['roster_id']}")
    
    # Get the 2025 league draft
    league_2025 = "1181025001438806016"
    from draft_service import DraftService
    draft_service = DraftService(client)
    
    drafts = draft_service.get_league_drafts(league_2025)
    if drafts:
        draft_order_raw = drafts[0].get('draft_order', {})
        
        print("\nDraft order (user_id -> position):")
        for user_id, position in draft_order_raw.items():
            if position == 10:  # emanueljd3's position
                print(f"  Position 10: user_id={user_id}")
                
                # Get the user's display name
                users = client.league_service.get_league_users(league_2025)
                for user in users:
                    if user.user_id == user_id:
                        print(f"  Position 10 belongs to: {user.display_name}")
                        break
        
        print("\nThe issue is that roster_id=7 in the pick data")
        print("But emanueljd3 has draft position 10, not 7")
        print("\nIn 2023, emanueljd3 had roster_id=7")
        print("In 2025 draft, emanueljd3 has position=10")
        print("\nThe fix needs to map based on user identity, not roster ID")

if __name__ == "__main__":
    debug_roster_mapping()