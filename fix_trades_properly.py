#!/usr/bin/env python3
"""
Fix trades to show newest first and correct team names
"""
import re
from datetime import datetime

def fix_trades():
    # Read current index.html
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract all trade items
    trades = []
    pattern = r'<div class="trade-item">.*?</div>\s*</div>\s*</div>'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for match in matches:
        # Extract date
        date_match = re.search(r'<div class="trade-date">(.*?)</div>', match)
        if date_match:
            date_str = date_match.group(1)
            try:
                # Parse the date
                date_obj = datetime.strptime(date_str, '%Y-%m-%d %I:%M %p')
                trades.append((date_obj, match))
            except:
                print(f"Could not parse date: {date_str}")
    
    # Sort by date descending (newest first)
    trades.sort(key=lambda x: x[0], reverse=True)
    print(f"Found {len(trades)} trades")
    
    # Find the timeline container
    timeline_start = content.find('<div class="timeline-container">')
    timeline_end = content.find('</div>', timeline_start)
    
    # Find where trades start and end
    first_trade = content.find('<div class="trade-item">', timeline_start)
    last_trade_end = timeline_start
    for match in matches:
        pos = content.rfind(match)
        if pos > last_trade_end:
            last_trade_end = pos + len(match)
    
    # Rebuild the timeline section
    new_timeline = '<div class="timeline-container">\n'
    for date_obj, trade_html in trades:
        new_timeline += '                    ' + trade_html + '\n'
    new_timeline += '                </div>'
    
    # Replace the old timeline with the new one
    before = content[:timeline_start]
    after = content[content.find('</div>', last_trade_end):]
    after = after[after.find('\n'):]  # Skip the closing div we already added
    
    new_content = before + new_timeline + after
    
    # Fix any remaining wrong team names
    new_content = new_content.replace('ItsAShow', 'ShadyCommish88')
    new_content = new_content.replace('Teehuss', 'emanueljd3')
    
    # Write back
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Fixed trade sorting - newest trades now appear first")
    print("✅ Fixed team names")

if __name__ == "__main__":
    fix_trades()