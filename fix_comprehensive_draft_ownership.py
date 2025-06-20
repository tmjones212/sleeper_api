#!/usr/bin/env python3
"""
Comprehensively fix ALL 2025 draft pick ownership issues
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

def fix_all_draft_ownership():
    # Load correct data
    pick_data = load_draft_data()
    
    # Read current index.html
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and fix all 2025 pick entries
    pick_pattern = re.compile(r'Pick #(\d+) \(([^\']+)\'s (\d{4}) R(\d)\) - ([^<]+)')
    
    fixes_made = 0
    
    def replace_pick(match):
        nonlocal fixes_made
        pick_num = int(match.group(1))
        stated_owner = match.group(2)
        year = match.group(3)
        round_num = int(match.group(4))
        player = match.group(5).strip()
        
        if year == '2025' and pick_num in pick_data:
            correct_owner = pick_data[pick_num]['original_owner']
            if stated_owner != correct_owner:
                fixes_made += 1
                return f'Pick #{pick_num} ({correct_owner}\'s {year} R{round_num}) - {player}'
        
        return match.group(0)  # No change needed
    
    # Apply the replacements
    new_content = pick_pattern.sub(replace_pick, content)
    
    # Write the fixed content
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Fixed {fixes_made} draft pick ownership issues")
    
    # Verify by running a quick audit
    print("\n=== VERIFICATION ===")
    
    # Check a few key picks
    key_checks = [
        (1, "caviar89", "TRAVIS HUNTER"),
        (4, "lamjohnson56", "CAM WARD"), 
        (6, "EBao", "QUINSHON JUDKINS"),
        (22, "Halteclere", "SHEDEUR SANDERS")
    ]
    
    for pick_num, expected_owner, player in key_checks:
        correct_pattern = f'Pick #{pick_num} ({expected_owner}\'s 2025'
        count = new_content.count(correct_pattern)
        if count > 0:
            print(f"✅ Pick #{pick_num} ({player}): Found {count} correct entries for {expected_owner}")
        else:
            print(f"❌ Pick #{pick_num} ({player}): No correct entries found for {expected_owner}")

if __name__ == "__main__":
    fix_all_draft_ownership()