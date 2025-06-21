#!/usr/bin/env python3
import re

def count_divs_in_structure(filename):
    """Count expected divs based on structure."""
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Expected structure for matchups panel:
    # 1. <div class="visualization-panel" id="matchups-panel">
    # 2.   <div class="panel-header">...</div>
    # 3.   <div class="panel-content">
    # 4.     <div class="search-container">...</div>
    # 5.     <div style="margin: 20px 0;">  (Head-to-Head section)
    # 6.       <h3>...</h3>
    # 7.       <div style="background: #2d2d2d...">  (table container)
    # 8.         <table>...</table>
    # 9.       </div>
    # 10.    </div>
    # 11.    <div id="matchupsContainer">
    # 12.      ... (matchup content)
    # 13.    </div>
    # 14.  </div>
    # 15. </div>
    
    print("Expected closing divs for proper structure:")
    print("1. Close matchupsContainer")
    print("2. Close panel-content") 
    print("3. Close visualization-panel")
    print("\nTotal expected closing divs at end of matchups panel: 3")
    
    # Now let's trace the actual structure
    matchups_start = content.find('id="matchups-panel"')
    if matchups_start == -1:
        print("Matchups panel not found!")
        return
    
    # Find where draft panel starts
    draft_start = content.find('id="draft-panel"', matchups_start)
    
    # Count actual structure between panels
    section = content[matchups_start:draft_start]
    
    # Count main structural elements
    panel_header = section.count('class="panel-header"')
    panel_content = section.count('class="panel-content"')
    matchups_container = section.count('id="matchupsContainer"')
    
    print(f"\nActual structure found:")
    print(f"- panel-header divs: {panel_header}")
    print(f"- panel-content divs: {panel_content}")
    print(f"- matchupsContainer divs: {matchups_container}")

count_divs_in_structure('index.html')

# Also check what's in those 8 closing divs
print("\n\nChecking the 8 closing divs at the end:")
with open('index.html', 'r') as f:
    lines = f.readlines()

# Look at wider context
for i in range(14310, 14330):
    if '</div>' in lines[i-1]:
        # Try to figure out what this div was closing
        # Look back for potential opening
        print(f"Line {i}: {lines[i-1].strip()}")