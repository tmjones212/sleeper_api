#!/usr/bin/env python3
"""Analyze roster history to understand the emanueljd3/connerstafford11 situation."""

import sys
sys.path.append('src')
from client import SleeperAPI
import json

def analyze_roster_history():
    client = SleeperAPI()
    
    # Check different league years
    league_years = {
        2025: "1181025001438806016",
        2024: "1048308938824937472",
        2023: "916445745966915584",
        2022: "839251409999347712"
    }
    
    print("=== Roster ID 10 ownership history ===\n")
    
    for year, league_id in sorted(league_years.items()):
        try:
            rosters = client.league_service.get_league_rosters(league_id)
            users = client.league_service.get_league_users(league_id)
            
            for roster in rosters:
                if roster.roster_id == 10:
                    user = next((u for u in users if u.user_id == roster.owner_id), None)
                    if user:
                        print(f"{year}: Roster 10 = {user.display_name}")
                    else:
                        print(f"{year}: Roster 10 = No owner")
                    break
        except:
            print(f"{year}: Could not get data")
    
    # Now check the problematic trade transaction directly
    print("\n=== Checking specific transaction ===")
    
    # Get the 2025 league transactions
    league_id = "1181025001438806016"
    all_trans = client.transaction_service.get_all_league_transactions(league_id)
    
    # Find the trade from 2023-04-07 that incorrectly assigns pick #1
    for trans in all_trans:
        if (trans.get('created_datetime') == '2023-04-07 11:22 AM' and 
            trans['type'] == 'trade' and 
            trans.get('draft_picks')):
            print(f"\nFound the trade from {trans['created_datetime']}")
            print(f"Transaction ID: {trans.get('transaction_id')}")
            
            for pick in trans['draft_picks']:
                if pick['season'] == '2025' and pick['round'] == 1:
                    print(f"\nDraft pick data:")
                    print(json.dumps(pick, indent=2))
                    
                    # Check what roster_id this is
                    print(f"\nThis pick has roster_id: {pick.get('roster_id')}")
                    print(f"Previous owner ID: {pick.get('previous_owner_id')}")
                    print(f"Current owner ID: {pick.get('owner_id')}")

if __name__ == "__main__":
    analyze_roster_history()