#!/usr/bin/env python3
"""
Fix all draft pick ownership issues comprehensively based on actual draft data
"""

import json
from bs4 import BeautifulSoup
import re

def load_draft_data():
    """Load the draft cache to get correct original owners"""
    with open('data/draft_cache.json', 'r') as f:
        draft_cache = json.load(f)
    
    # Create lookup: pick_number -> original_owner
    pick_to_owner = {}
    for pick in draft_cache['drafts_by_year']['2025'][0]['picks']:
        pick_to_owner[pick['overall_pick']] = {
            'original_owner': pick['original_owner'],
            'player_name': pick['player_name'],
            'round': pick['round']
        }
    
    return pick_to_owner

def fix_draft_pick_ownership():
    # Load draft data
    pick_to_owner = load_draft_data()
    
    # Read current index.html
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # Track all fixes made
    fixes_made = []
    
    # Find all pick items with pick numbers
    pick_pattern = re.compile(r'Pick #(\d+) \(([^\']+)\'s (\d{4}) R(\d)\) - (.+)')
    
    # Process all trade items
    for trade_item in soup.find_all('div', class_='trade-item'):
        # Find all pick items in this trade
        for li in trade_item.find_all('li', class_='pick-item'):
            if li.string:
                match = pick_pattern.match(li.string)
                if match:
                    pick_num = int(match.group(1))
                    current_owner = match.group(2)
                    year = match.group(3)
                    round_num = int(match.group(4))
                    player = match.group(5)
                    
                    if year == '2025' and pick_num in pick_to_owner:
                        correct_data = pick_to_owner[pick_num]
                        correct_owner = correct_data['original_owner']
                        
                        if current_owner != correct_owner:
                            # Fix the ownership
                            old_text = li.string
                            new_text = f"Pick #{pick_num} ({correct_owner}'s 2025 R{round_num}) - {player}"
                            li.string = new_text
                            
                            fixes_made.append({
                                'pick': pick_num,
                                'old_owner': current_owner,
                                'correct_owner': correct_owner,
                                'player': player
                            })
    
    # Write the fixed content
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(str(soup))
    
    # Print summary of fixes
    print("=== DRAFT PICK OWNERSHIP FIXES ===\n")
    
    if fixes_made:
        for fix in fixes_made:
            print(f"Pick #{fix['pick']} ({fix['player']}):")
            print(f"  Changed from: {fix['old_owner']}")
            print(f"  Changed to: {fix['correct_owner']}")
            print()
    else:
        print("No ownership fixes needed!")
    
    print(f"\nTotal fixes made: {len(fixes_made)}")
    
    # Also check for picks without owners that should have them
    print("\n=== CHECKING FOR PICKS WITHOUT OWNERSHIP ===")
    
    # Re-read to check for generic picks
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    generic_pattern = re.compile(r'📋 (\d{4}) Round (\d) pick</li>')
    generic_matches = generic_pattern.findall(content)
    
    if generic_matches:
        print(f"\nFound {len(generic_matches)} picks without ownership info:")
        for year, round_num in generic_matches:
            print(f"  - {year} Round {round_num} pick")
        print("\nThese may need additional investigation")
    else:
        print("\n✅ All picks have ownership information")

if __name__ == "__main__":
    fix_draft_pick_ownership()