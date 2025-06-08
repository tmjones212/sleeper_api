#!/usr/bin/env python3
"""Find emanueljd3's roster ID."""

import sys
sys.path.append('src')
from client import SleeperAPI

def find_emanueljd3_roster():
    client = SleeperAPI()
    
    league_years = {
        2025: "1181025001438806016",
        2024: "1048308938824937472", 
        2023: "916445745966915584",
        2022: "839251409999347712"
    }
    
    print("=== Searching for emanueljd3 ===\n")
    
    for year, league_id in sorted(league_years.items(), reverse=True):
        try:
            rosters = client.league_service.get_league_rosters(league_id)
            users = client.league_service.get_league_users(league_id)
            
            print(f"\n{year} League ({league_id}):")
            found = False
            for roster in rosters:
                user = next((u for u in users if u.user_id == roster.owner_id), None)
                if user and 'emanueljd3' in user.display_name.lower():
                    print(f"  Found! Roster ID {roster.roster_id} = {user.display_name}")
                    found = True
            
            if not found:
                print("  emanueljd3 not found in this league")
                # List all teams to see what's there
                print("  All teams:")
                for roster in sorted(rosters, key=lambda x: x.roster_id):
                    user = next((u for u in users if u.user_id == roster.owner_id), None)
                    if user:
                        print(f"    Roster {roster.roster_id}: {user.display_name}")
                    
        except Exception as e:
            print(f"{year}: Error - {e}")

if __name__ == "__main__":
    find_emanueljd3_roster()