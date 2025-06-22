#!/usr/bin/env python3
import re

with open('index.html', 'r') as f:
    content = f.read()

# Find all panel starts
panels = ['overview', 'network', 'matrix', 'timeline', 'players', 'matchups', 'draft']
for panel in panels:
    pattern = f'<div class="visualization-panel" id="{panel}-panel">'
    pos = content.find(pattern)
    if pos != -1:
        line_num = content[:pos].count('\n') + 1
        print(f"{panel}-panel starts at line {line_num}")
        
        # Check if it's inside another panel
        before_content = content[:pos]
        open_panels = before_content.count('<div class="visualization-panel"')
        close_panels = before_content.count('</div> <!-- End of') + before_content.count('-panel -->')
        
        # Count panel-specific closes
        for p in panels:
            close_panels += before_content.count(f'<!-- End of {p}-panel -->')
            close_panels += before_content.count(f'<!-- {p}-panel -->')
        
        if open_panels > close_panels:
            print(f"  ⚠️  WARNING: {panel}-panel might be nested! Open panels: {open_panels}, Closed: {close_panels}")
        else:
            print(f"  ✓ Structure looks OK")
    else:
        print(f"❌ {panel}-panel NOT FOUND!")

# Special check for matchups
matchups_pos = content.find('id="matchups-panel"')
if matchups_pos != -1:
    # Find previous panel div
    prev_panel = content.rfind('<div class="visualization-panel"', 0, matchups_pos)
    if prev_panel != -1:
        prev_text = content[prev_panel:prev_panel+100]
        print(f"\nPanel before matchups: {prev_text[:50]}...")
        
    # Check parent chain
    check_pos = matchups_pos
    parents = []
    while check_pos > 0:
        div_start = content.rfind('<div', 0, check_pos)
        if div_start == -1:
            break
        div_text = content[div_start:content.find('>', div_start)+1]
        if 'class="visualization-panel"' in div_text and 'matchups-panel' not in div_text:
            parents.append(div_text)
        check_pos = div_start - 1
        if len(parents) > 3:
            break
    
    if parents:
        print("\n⚠️  Other visualization-panels in parent chain:")
        for p in parents:
            print(f"  {p}")