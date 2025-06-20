#!/usr/bin/env python3
"""
Fix all draft pick ownership issues by directly replacing incorrect entries
"""

import json

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
    
    # Define the specific fixes we need to make
    fixes = [
        # Fix Pick #6 - should be EBao's, not lamjohnson56's or ShadyCommish88's
        {
            'old': '<li class="pick-item">📋 Pick #6 (lamjohnson56\'s 2025 R1) - QUINSHON JUDKINS</li>',
            'new': '<li class="pick-item">📋 Pick #6 (EBao\'s 2025 R1) - QUINSHON JUDKINS</li>'
        },
        {
            'old': '<li class="pick-item">📋 Pick #6 (ShadyCommish88\'s 2025 R1) - QUINSHON JUDKINS</li>',
            'new': '<li class="pick-item">📋 Pick #6 (EBao\'s 2025 R1) - QUINSHON JUDKINS</li>'
        },
        # Fix Pick #22 - should be Halteclere's, not caviar89's
        {
            'old': '<li class="pick-item">📋 Pick #22 (caviar89\'s 2025 R3) - SHEDEUR SANDERS</li>',
            'new': '<li class="pick-item">📋 Pick #22 (Halteclere\'s 2025 R3) - SHEDEUR SANDERS</li>'
        }
    ]
    
    # Apply fixes
    fixes_made = 0
    for fix in fixes:
        count = content.count(fix['old'])
        if count > 0:
            content = content.replace(fix['old'], fix['new'])
            fixes_made += count
            print(f"Fixed {count} instance(s) of: {fix['old'][:50]}...")
    
    # Write the fixed content
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ Total fixes made: {fixes_made}")
    
    # Verify the fixes
    print("\n=== VERIFICATION ===")
    
    # Check Pick #6 entries
    pick6_lines = []
    pick22_lines = []
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'Pick #6' in line and '2025 R1' in line and 'QUINSHON JUDKINS' in line:
            pick6_lines.append((i+1, line.strip()))
        elif 'Pick #22' in line and '2025 R3' in line and 'SHEDEUR SANDERS' in line:
            pick22_lines.append((i+1, line.strip()))
    
    print("\nPick #6 (QUINSHON JUDKINS) entries:")
    for line_num, line in pick6_lines:
        if "EBao's" in line:
            print(f"  ✅ Line {line_num}: Correct owner (EBao)")
        else:
            print(f"  ❌ Line {line_num}: INCORRECT - {line}")
    
    print("\nPick #22 (SHEDEUR SANDERS) entries:")
    for line_num, line in pick22_lines:
        if "Halteclere's" in line:
            print(f"  ✅ Line {line_num}: Correct owner (Halteclere)")
        else:
            print(f"  ❌ Line {line_num}: INCORRECT - {line}")

if __name__ == "__main__":
    fix_draft_pick_ownership()