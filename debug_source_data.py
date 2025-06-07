#!/usr/bin/env python3

import json
from datetime import datetime

# Load transaction data
with open('data/league_1181025001438806016_transactions.json', 'r') as f:
    transactions = json.load(f)

# Find the specific trade (2024-11-01 08:40 AM = timestamp around 1730455200000)
target_trade = None
for t in transactions:
    if t['type'] == 'trade':
        dt = datetime.fromtimestamp(t['status_updated'] / 1000)
        if dt.strftime('%Y-%m-%d %I:%M %p') == '2024-11-01 08:40 AM':
            target_trade = t
            break

if not target_trade:
    print("Target trade not found")
    exit(1)

print("Found target trade:")
print(f"Date: {datetime.fromtimestamp(target_trade['status_updated'] / 1000).strftime('%Y-%m-%d %I:%M %p')}")
print(f"Status: {target_trade['status']}")
print(f"Type: {target_trade['type']}")

print(f"\nDraft picks in transaction: {len(target_trade.get('draft_picks', []))}")
for i, pick in enumerate(target_trade.get('draft_picks', [])):
    print(f"Pick {i+1}:")
    print(f"  Round: {pick['round']}")
    print(f"  Season: {pick['season']}")
    print(f"  Owner ID: {pick['owner_id']}")
    print(f"  Previous Owner ID: {pick['previous_owner_id']}")
    print(f"  Roster ID: {pick.get('roster_id', 'N/A')}")
    print()

# Count duplicates in source
pick_counts = {}
for pick in target_trade.get('draft_picks', []):
    key = f"R{pick['round']}-{pick['season']}-{pick['owner_id']}-{pick['previous_owner_id']}"
    pick_counts[key] = pick_counts.get(key, 0) + 1

duplicates = {k: v for k, v in pick_counts.items() if v > 1}
if duplicates:
    print(f"DUPLICATES IN SOURCE DATA: {duplicates}")
else:
    print("No duplicates in source transaction data")