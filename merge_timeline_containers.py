#!/usr/bin/env python3
"""
Merge the two separate timeline containers into one
"""
import re

def merge_timelines():
    # Read current index.html
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all trade-item divs
    all_trades = []
    pattern = r'<div class="trade-item">.*?</div>\s*</div>\s*</div>'
    matches = re.findall(pattern, content, re.DOTALL)
    
    print(f"Found {len(matches)} total trades")
    
    # Extract dates from each trade for sorting
    trades_with_dates = []
    for match in matches:
        date_match = re.search(r'<div class="trade-date">(\d{4}-\d{2}-\d{2} \d{2}:\d{2} [AP]M)</div>', match)
        if date_match:
            date_str = date_match.group(1)
            trades_with_dates.append((date_str, match))
    
    # Sort by date descending
    from datetime import datetime
    trades_with_dates.sort(key=lambda x: datetime.strptime(x[0], '%Y-%m-%d %I:%M %p'), reverse=True)
    
    # Find the first timeline container
    timeline_start = content.find('<div class="timeline-container">')
    if timeline_start == -1:
        print("ERROR: No timeline container found")
        return
    
    # Find the end of all timeline content (including any duplicate containers)
    # Look for the closing of the trade history section
    section_end = content.find('</div>\n\n        <h2 class="panel-header">', timeline_start)
    if section_end == -1:
        # Try another pattern
        section_end = content.find('</div>\n        </div>\n\n        <!-- Network Panel -->', timeline_start)
    if section_end == -1:
        print("ERROR: Could not find end of trade history section")
        return
    
    # Build the new single timeline
    new_timeline = '<div class="timeline-container">\n'
    for date, trade in trades_with_dates:
        new_timeline += '                    ' + trade.strip() + '\n'
    new_timeline += '                </div>'
    
    # Replace everything from timeline start to section end
    new_content = content[:timeline_start] + new_timeline + content[section_end:]
    
    # Write back
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Merged all trades into a single timeline container")
    print(f"✅ Total trades: {len(trades_with_dates)}")

if __name__ == "__main__":
    merge_timelines()