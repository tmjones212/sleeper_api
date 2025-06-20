#!/usr/bin/env python3
"""
Fix duplicate trades in index.html by removing exact duplicates
Version 2 - Better pattern matching
"""
import re
from datetime import datetime
import shutil

def find_and_remove_duplicates():
    # Read the HTML file
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create backup
    backup_name = f'index_backup_duplicate_fix_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
    shutil.copy('index.html', backup_name)
    print(f"Created backup: {backup_name}")
    
    # Find the timeline panel section
    timeline_start = content.find('<div class="visualization-panel" id="timeline-panel">')
    if timeline_start == -1:
        print("ERROR: Could not find timeline panel")
        return
    
    # Find the next visualization panel (player journey panel)
    timeline_end = content.find('<div class="visualization-panel" id="players-panel">', timeline_start)
    if timeline_end == -1:
        print("ERROR: Could not find end of timeline panel")
        return
    
    # Extract timeline section
    before = content[:timeline_start]
    timeline_section = content[timeline_start:timeline_end]
    after = content[timeline_end:]
    
    print(f"Timeline section length: {len(timeline_section)}")
    
    # Extract all trade-item divs
    trade_items = []
    seen_keys = set()
    unique_trades = []
    
    # Find all trade items using a simpler approach
    pos = 0
    while True:
        start = timeline_section.find('<div class="trade-item">', pos)
        if start == -1:
            break
        
        # Find the corresponding closing div by counting divs
        div_count = 0
        end = start
        while end < len(timeline_section):
            if timeline_section[end:end+4] == '<div':
                div_count += 1
            elif timeline_section[end:end+6] == '</div>':
                div_count -= 1
                if div_count == 0:
                    end += 6
                    break
            end += 1
        
        if end > len(timeline_section):
            break
        
        trade_html = timeline_section[start:end]
        trade_items.append((start, end, trade_html))
        
        # Extract key info to identify duplicates
        date_match = re.search(r'<div class="trade-date">(.*?)</div>', trade_html)
        teams_match = re.search(r'<strong>(.*?)</strong>', trade_html)
        
        if date_match and teams_match:
            key = f"{date_match.group(1)}|{teams_match.group(1)}"
            
            if key not in seen_keys:
                seen_keys.add(key)
                unique_trades.append((start, end, trade_html))
            else:
                print(f"Found duplicate: {key}")
        
        pos = end
    
    print(f"Found {len(trade_items)} total trades")
    print(f"Keeping {len(unique_trades)} unique trades")
    
    if len(trade_items) == len(unique_trades):
        print("No duplicates found!")
        return
    
    # Rebuild timeline section with only unique trades
    # Find the timeline-container div
    container_start = timeline_section.find('<div class="timeline-container">')
    container_end = timeline_section.rfind('</div>')  # Last closing div before players panel
    
    # Build new timeline section
    new_timeline = timeline_section[:container_start + len('<div class="timeline-container">')] + '\n'
    
    # Add the opening pattern that appears in the original
    if 'ALWAYS SHOW NEW TRADES' in timeline_section:
        pattern_start = timeline_section.find('<!-- ALWAYS SHOW NEW TRADES')
        pattern_end = timeline_section.find('-->', pattern_start) + 3
        if pattern_start > -1:
            new_timeline += '                    ' + timeline_section[pattern_start:pattern_end] + '\n'
    
    # Add unique trades
    for _, _, trade in unique_trades:
        new_timeline += '                    ' + trade + '\n\n'
    
    # Close the timeline container
    new_timeline += '                </div>\n            </div>\n        </div>\n\n'
    
    # Write the updated content
    new_content = before + new_timeline + after
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Successfully removed duplicate trades!")

if __name__ == "__main__":
    find_and_remove_duplicates()