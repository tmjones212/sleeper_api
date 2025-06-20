#!/usr/bin/env python3

import sys
sys.path.append('./src')

from transaction_service import TransactionService
from client import SleeperAPI
import json

# Create the transaction service
league_id = '1181025001438806016'
client = SleeperAPI(league_id)
service = TransactionService(client)

# Get all transactions
transactions_file = f'src/data/league_{league_id}_transactions.json'
with open(transactions_file, 'r') as f:
    transactions = json.load(f)

# Find the specific problematic trade (created: 1749776353830)
target_trade = None
for transaction in transactions:
    if transaction.get('created') == 1749776353830:
        target_trade = transaction
        break

if target_trade:
    print("Found the problematic trade:")
    print(f"Date: {target_trade.get('datetime', 'N/A')}")
    print(f"Transaction ID: {target_trade.get('transaction_id', 'N/A')}")
    print(f"Teams: {target_trade.get('roster_names', [])}")
    print("\nDraft picks in this trade:")
    
    for i, pick in enumerate(target_trade.get('draft_picks', [])):
        print(f"\nPick {i+1}:")
        print(f"  Round: {pick['round']}")
        print(f"  Season: {pick['season']}")
        print(f"  roster_id: {pick['roster_id']}")
        print(f"  owner_id: {pick['owner_id']}")
        print(f"  previous_owner_id: {pick['previous_owner_id']}")
        
        # Get roster to team mapping
        league = client.league_service.get_league(league_id, fetch_all=True)
        roster_to_team = {team.roster.roster_id: team.display_name for team in league.teams if team.roster}
        
        # Test the original owner lookup
        original_roster_id = pick.get('roster_id', pick['previous_owner_id'])
        original_owner = service._get_historical_team_name(original_roster_id, pick['season'], league_id, roster_to_team)
        
        print(f"  original_roster_id: {original_roster_id}")
        print(f"  calculated original_owner: '{original_owner}'")
        print(f"  roster_to_team mapping: {roster_to_team}")
else:
    print("Could not find the problematic trade!")