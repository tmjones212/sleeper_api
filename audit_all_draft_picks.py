#!/usr/bin/env python3
"""
Audit all 2025 draft picks to find any other incorrect ownership
"""

import json
import re

def load_draft_data():
    """Load the draft cache to get correct original owners"""
    with open('data/draft_cache.json', 'r') as f:
        draft_cache = json.load(f)
    
    # Create lookup: pick_number -> data
    pick_data = {}
    for pick in draft_cache['drafts_by_year']['2025'][0]['picks']:
        pick_data[pick['overall_pick']] = {
            'original_owner': pick['original_owner'],
            'player_name': pick['player_name'],
            'round': pick['round'],
            'pick_in_round': pick['pick_in_round']
        }
    
    return pick_data

def audit_picks():
    # Load correct data
    pick_data = load_draft_data()
    
    # Read current index.html
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all pick entries with pattern: Pick #N (Owner's YYYY RX) - PLAYER
    pick_pattern = re.compile(r'Pick #(\d+) \(([^\']+)\'s (\d{4}) R(\d)\) - ([^<]+)')
    
    issues = []
    
    for match in pick_pattern.finditer(content):
        pick_num = int(match.group(1))
        stated_owner = match.group(2)
        year = match.group(3)
        round_num = int(match.group(4))
        player = match.group(5).strip()
        
        if year == '2025' and pick_num in pick_data:
            correct_data = pick_data[pick_num]
            correct_owner = correct_data['original_owner']
            correct_player = correct_data['player_name']
            
            if stated_owner != correct_owner:
                issues.append({
                    'pick': pick_num,
                    'stated_owner': stated_owner,
                    'correct_owner': correct_owner,
                    'player': player,
                    'line': match.group(0)
                })
    
    # Print findings
    print("=== 2025 DRAFT PICK OWNERSHIP AUDIT ===\n")
    
    if issues:
        print(f"Found {len(issues)} picks with incorrect ownership:\n")
        
        # Group by pick number
        by_pick = {}
        for issue in issues:
            pick_num = issue['pick']
            if pick_num not in by_pick:
                by_pick[pick_num] = []
            by_pick[pick_num].append(issue)
        
        for pick_num in sorted(by_pick.keys()):
            pick_issues = by_pick[pick_num]
            print(f"Pick #{pick_num} ({pick_issues[0]['player']}):")
            print(f"  Correct owner: {pick_issues[0]['correct_owner']}")
            print(f"  Found with wrong owner(s):")
            for issue in pick_issues:
                print(f"    - Listed as: {issue['stated_owner']}")
            print()
    else:
        print("✅ All 2025 draft picks have correct ownership!")
    
    # Also check for key draft positions
    print("\n=== KEY DRAFT POSITION VERIFICATION ===")
    key_positions = {
        1: "caviar89",      # 1st overall
        4: "lamjohnson56",  # 4th overall (mentioned as correct by user)
        6: "EBao",          # 6th overall
        22: "Halteclere"    # 22nd overall (round 3)
    }
    
    for pick_num, expected_owner in key_positions.items():
        if pick_num in pick_data:
            actual = pick_data[pick_num]['original_owner']
            player = pick_data[pick_num]['player_name']
            if actual == expected_owner:
                print(f"✅ Pick #{pick_num} ({player}): Correctly owned by {expected_owner}")
            else:
                print(f"❌ Pick #{pick_num} ({player}): Should be {expected_owner}, not {actual}")

if __name__ == "__main__":
    audit_picks()