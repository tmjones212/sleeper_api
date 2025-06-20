#!/usr/bin/env python3
"""
Check for trades with duplicate content but different structure
"""
import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all trades with DJ Moore or specific dates
dj_moore_trades = []
pattern = r'<div class="trade-item">.*?</div>\s*</div>\s*</div>'

# Look for trades containing DJ Moore or the specific date/teams
pos = 0
while True:
    match = re.search(r'<div class="trade-item">', content[pos:])
    if not match:
        break
    
    start = pos + match.start()
    
    # Find the end by counting divs
    div_count = 0
    end = start
    while end < len(content):
        if content[end:end+4] == '<div':
            div_count += 1
        elif content[end:end+6] == '</div>':
            div_count -= 1
            if div_count == 0:
                end += 6
                break
        end += 1
    
    trade_html = content[start:end]
    
    # Check if this trade contains DJ Moore or the specific pattern
    if ('DJ MOORE' in trade_html or 
        ('2025-06-12' in trade_html and 'emanueljd3' in trade_html) or
        ('ShadyCommish88' in trade_html and 'emanueljd3' in trade_html and '2 picks' in trade_html)):
        
        # Extract key details
        date_match = re.search(r'<div class="trade-date">(.*?)</div>', trade_html)
        teams_match = re.search(r'<strong>(.*?)</strong>', trade_html)
        
        date = date_match.group(1) if date_match else "No date"
        teams = teams_match.group(1) if teams_match else "No teams"
        
        # Check if it has proper team structure or not
        has_team_structure = '<div class="team-side">' in trade_html
        
        print(f"\nFound potential duplicate:")
        print(f"  Date: {date}")
        print(f"  Teams: {teams}")
        print(f"  Has proper team structure: {has_team_structure}")
        print(f"  Position in file: {start}")
        
        # Show a snippet
        if 'DJ MOORE' in trade_html:
            print("  Contains: DJ MOORE")
        if 'Round 2 pick' in trade_html:
            print("  Contains: Draft picks")
    
    pos = end

print("\nDone checking.")