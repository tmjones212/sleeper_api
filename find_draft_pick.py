#!/usr/bin/env python3
"""Find the actual draft pick for mlum20/caviar89 in 2024"""

import re
import json

def find_2024_pick():
    with open('index.html', 'r') as f:
        content = f.read()
    
    # Look for 2024 draft data in the draftData object
    match = re.search(r'"2024": \[(.*?)\]', content, re.DOTALL)
    if match:
        draft_2024_str = match.group(1)
        
        # Find all picks with their details
        pick_pattern = r'"overall_pick": (\d+),.*?"original_owner": "([^"]*)",.*?"player_name": "([^"]*)",.*?"team": "([^"]*)"'
        picks = re.findall(pick_pattern, draft_2024_str, re.DOTALL)
        
        print("2024 Draft Picks involving mlum20/caviar89/Team 9:")
        for pick_num, orig_owner, player, team in picks:
            if 'mlum20' in orig_owner.lower() or 'mlum20' in team.lower() or \
               'caviar89' in orig_owner.lower() or 'caviar89' in team.lower() or \
               'team 9' in orig_owner.lower() or orig_owner == 'Team 9':
                print(f"Pick #{pick_num}: {player} - Original: {orig_owner}, Team: {team}")
        
        # Also check the current transaction data for roster_id 9 mapping
        print("\nAll first round picks (1-12):")
        for pick_num, orig_owner, player, team in picks:
            if int(pick_num) <= 12:
                print(f"Pick #{pick_num}: {player} - Original: {orig_owner}, Team: {team}")

if __name__ == "__main__":
    find_2024_pick()