#!/usr/bin/env python3
"""
Fix the duplicate timeline container issue
"""
import re
from datetime import datetime

def fix_duplicate_timeline():
    # Read current index.html
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all instances of timeline-container
    timeline_positions = []
    pos = 0
    while True:
        pos = content.find('<div class="timeline-container">', pos)
        if pos == -1:
            break
        timeline_positions.append(pos)
        pos += 1
    
    print(f"Found {len(timeline_positions)} timeline containers at positions: {timeline_positions}")
    
    # Extract all trade items from the entire content
    all_trades = []
    trade_pattern = r'<div class="trade-item">.*?(?=<div class="trade-item">|</div>\s*</div>\s*(?:</div>|<h2|<!-- Network))'
    
    # Find all trades
    for match in re.finditer(trade_pattern, content, re.DOTALL):
        trade_html = match.group(0)
        # Make sure it's a complete trade
        if 'trade-date' in trade_html and 'trade-teams' in trade_html:
            # Clean up the trade HTML
            trade_html = trade_html.strip()
            # Ensure it ends properly
            if not trade_html.endswith('</div>'):
                # Count opening and closing divs
                open_divs = trade_html.count('<div')
                close_divs = trade_html.count('</div>')
                missing_closes = open_divs - close_divs
                trade_html += '</div>' * missing_closes
            
            # Extract date for sorting
            date_match = re.search(r'<div class="trade-date">(\d{4}-\d{2}-\d{2} \d{2}:\d{2} [AP]M)</div>', trade_html)
            if date_match:
                date_str = date_match.group(1)
                all_trades.append((date_str, trade_html))
    
    print(f"Found {len(all_trades)} trades total")
    
    # Sort by date descending
    all_trades.sort(key=lambda x: datetime.strptime(x[0], '%Y-%m-%d %I:%M %p'), reverse=True)
    
    # Find where to place the single timeline
    # Start from the first timeline container
    start_pos = content.find('<div class="timeline-container">')
    
    # Find the end - look for Network Panel section
    end_pos = content.find('<!-- Network Panel -->')
    if end_pos == -1:
        print("ERROR: Could not find Network Panel marker")
        return
    
    # Back up to find the proper closing divs before Network Panel
    search_pos = end_pos - 1
    while search_pos > start_pos:
        if content[search_pos:search_pos+6] == '</div>':
            # Check if this might be the end of our trade section
            test_str = content[search_pos-100:search_pos]
            if 'monthlyChart' in test_str or 'trade-grade' in test_str:
                end_pos = search_pos
                break
        search_pos -= 1
    
    # Build the new timeline section
    new_timeline = '<div class="timeline-container">\n'
    for date, trade in all_trades:
        new_timeline += '                    ' + trade + '\n'
    new_timeline += '                </div>'
    
    # Replace the entire section
    new_content = content[:start_pos] + new_timeline + content[end_pos:]
    
    # Write back
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Fixed duplicate timeline containers")
    print(f"✅ All {len(all_trades)} trades are now in a single timeline")
    print(f"✅ Newest trade: {all_trades[0][0]}")
    print(f"✅ Oldest trade: {all_trades[-1][0]}")

if __name__ == "__main__":
    fix_duplicate_timeline()