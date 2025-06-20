#!/usr/bin/env python3
from client import SleeperAPI
from datetime import datetime

league_id = "1181025001438806016"
client = SleeperAPI(league_id)

# Get all transactions
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

# Filter for trades after May 2, 2025
trades = [t for t in all_transactions if t.get('type') == 'trade']
trades.sort(key=lambda x: x.get('status_updated', 0), reverse=True)

may_2_2025 = datetime(2025, 5, 2, 23, 59, 59).timestamp() * 1000

print("New trades after May 2, 2025:")
for i, trade in enumerate(trades):
    if trade.get('status_updated', 0) > may_2_2025:
        trade_date = datetime.fromtimestamp(trade['status_updated'] / 1000)
        print(f"{i+1}. {trade_date.strftime('%Y-%m-%d %I:%M %p')}")
        
        # Print team names
        if trade.get('roster_names'):
            teams = trade['roster_names']
            print(f"   Teams: {' ↔ '.join(teams)}")
        
        # Count assets
        players = len(trade.get('adds', {}))
        picks = len(trade.get('draft_picks', []))
        print(f"   Assets: {players} players, {picks} picks")
        print()
    else:
        break