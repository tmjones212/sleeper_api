#!/usr/bin/env python3
from client import SleeperAPI

# All league IDs
leagues = {
    "2025": "1181025001438806016",
    "2024": "1048308938824937472", 
    "2023": "916445745966915584"
}

# Update transactions for all leagues
for year, league_id in leagues.items():
    print(f"Updating transactions for {year} season (league {league_id})...")
    try:
        client = SleeperAPI(league_id)
        transactions = client.transaction_service.get_all_league_transactions(league_id)
        print(f"Successfully updated {len(transactions)} transactions for {year}")
        print(f"Transactions saved to: data/league_{league_id}_transactions.json")
    except Exception as e:
        print(f"Error updating {year} transactions: {e}")
    print("-" * 50)