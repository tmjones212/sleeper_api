#!/usr/bin/env python3
"""
Fix duplicate trades in index.html by removing exact duplicates
"""
import re
from collections import defaultdict

def extract_trade_items(html_content):
    """Extract all trade-item divs from HTML"""
    # Match from trade-item opening to the closing of trade-grade-container div
    trade_pattern = r'<div class="trade-item">.*?</div>\s*</div>'
    
    # Find all positions of trade-item divs
    trades = []
    start_pos = 0
    
    while True:
        # Find next trade-item
        trade_start = html_content.find('<div class="trade-item">', start_pos)
        if trade_start == -1:
            break
        
        # Find the end of this trade item (after trade-grade-container closes)
        # Count div openings and closings to find the matching close
        div_count = 0
        pos = trade_start
        
        while pos < len(html_content):
            if html_content[pos:pos+4] == '<div':
                div_count += 1
            elif html_content[pos:pos+6] == '</div>':
                div_count -= 1
                if div_count == 0:
                    # Found the matching close div
                    trade_end = pos + 6
                    trades.append(html_content[trade_start:trade_end])
                    start_pos = trade_end
                    break
            pos += 1
        
        if pos >= len(html_content):
            break
    
    return trades

def get_trade_key(trade_html):
    """Extract a unique key from trade HTML to identify duplicates"""
    # Extract date
    date_match = re.search(r'<div class="trade-date">(.*?)</div>', trade_html)
    date = date_match.group(1) if date_match else ""
    
    # Extract teams
    teams_match = re.search(r'<strong>(.*?)</strong>', trade_html)
    teams = teams_match.group(1) if teams_match else ""
    
    # Extract player/pick counts
    counts_match = re.search(r'(\d+) players, (\d+) picks', trade_html)
    counts = counts_match.groups() if counts_match else ("0", "0")
    
    # Create a key from date + teams + counts
    return f"{date}|{teams}|{counts[0]}|{counts[1]}"

def remove_duplicate_trades(html_content):
    """Remove duplicate trades from HTML content"""
    # Find the timeline container
    timeline_start = html_content.find('<div class="timeline-container">')
    
    if timeline_start == -1:
        print("ERROR: Could not find timeline container")
        return html_content
    
    # Find the end of timeline container by looking for the closing div
    # that matches the timeline-container div
    div_count = 0
    pos = timeline_start
    timeline_end = -1
    
    while pos < len(html_content):
        if html_content[pos:pos+4] == '<div':
            div_count += 1
        elif html_content[pos:pos+6] == '</div>':
            div_count -= 1
            if div_count == 0:
                timeline_end = pos + 6
                break
        pos += 1
    
    if timeline_end == -1:
        print("ERROR: Could not find end of timeline container")
        return html_content
    
    # Extract the content before and after timeline
    before_timeline = html_content[:timeline_start]
    timeline_content = html_content[timeline_start:timeline_end]
    after_timeline = html_content[timeline_end:]
    
    print(f"Timeline content length: {len(timeline_content)}")
    
    # Extract all trade items
    trades = extract_trade_items(timeline_content)
    print(f"Found {len(trades)} total trade items")
    
    # Track unique trades
    seen_trades = {}
    unique_trades = []
    
    for trade in trades:
        trade_key = get_trade_key(trade)
        
        if trade_key not in seen_trades:
            seen_trades[trade_key] = trade
            unique_trades.append(trade)
        else:
            print(f"Found duplicate trade: {trade_key}")
    
    print(f"Keeping {len(unique_trades)} unique trades")
    
    # Rebuild timeline content
    new_timeline = '<div class="timeline-container">\n                    \n'
    
    # Add unique trades back
    for trade in unique_trades:
        new_timeline += '                    ' + trade + '\n\n'
    
    new_timeline += '                </div>'
    
    # Reconstruct full HTML
    return before_timeline + new_timeline + after_timeline

def main():
    print("Fixing duplicate trades in index.html...")
    
    # Read current HTML
    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Create backup
    import shutil
    from datetime import datetime
    backup_name = f'index_backup_duplicate_fix_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
    shutil.copy('index.html', backup_name)
    print(f"Created backup: {backup_name}")
    
    # Remove duplicates
    fixed_html = remove_duplicate_trades(html_content)
    
    # Write back
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(fixed_html)
    
    print("✅ Successfully removed duplicate trades!")

if __name__ == "__main__":
    main()