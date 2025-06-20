#!/usr/bin/env python3
import json
import re
from client import SleeperAPI

# 2025 league ID
league_id = "1181025001438806016"
print(f"Getting fresh trade data for league {league_id}...")

# Initialize client
client = SleeperAPI(league_id)

# Get transactions directly
all_transactions = []
week = 1

while True:
    try:
        transactions = client.league_service.get_league_transactions(league_id, week)
        if not transactions:
            break
        all_transactions.extend(transactions)
        week += 1
    except:
        break

print(f"Found {len(all_transactions)} total transactions")

# Filter for trades only
trades = [t for t in all_transactions if t.get('type') == 'trade']
print(f"Found {len(trades)} trades")

# Read the current index.html to extract the existing networkData format
with open('../index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Find the current networkData line to understand its structure
import re
match = re.search(r'const networkData = ({.*?});', html_content, re.DOTALL)
if match:
    # Parse the existing structure to understand format
    existing_data = match.group(1)
    
    # For now, let's just log that we found it
    print("Found existing networkData in index.html")
    print(f"Latest trade in new data: {trades[0]['created'] if trades else 'No trades'}")
    
    # Since the networkData structure is complex and your file has custom processing,
    # let's check if the trades are actually different
    if trades:
        latest_trade_timestamp = max(t.get('status_updated', 0) for t in trades)
        from datetime import datetime
        latest_date = datetime.fromtimestamp(latest_trade_timestamp / 1000)
        print(f"Latest trade date: {latest_date}")
        
        # Check if this is already in the HTML
        latest_date_str = latest_date.strftime('%Y-%m-%d')
        if latest_date_str in html_content:
            print("Latest trades already appear to be in the HTML!")
        else:
            print("New trades found that aren't in the HTML")
else:
    print("Could not find networkData in index.html")