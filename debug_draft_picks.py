#!/usr/bin/env python3
"""Debug script to trace draft pick processing"""
import sys
import requests
sys.path.append('src')

# Get raw API data first
draft_id = '1048308938824937473'  # 2024 draft
league_id = '1048308938824937472'  # 2024 league

print("=== RAW API DATA ===")
picks_url = f'https://api.sleeper.app/v1/draft/{draft_id}/picks'
api_picks = requests.get(picks_url).json()
print(f"Total picks from API: {len(api_picks)}")

problem_picks = [11, 21, 22, 31, 32, 33]  # Overall picks that are missing
print("\nProblem picks from API:")
for overall_pick in problem_picks:
    pick = next((p for p in api_picks if p['pick_no'] == overall_pick), None)
    if pick:
        print(f"  #{overall_pick}: R{pick['round']}, Roster {pick['roster_id']}, Player {pick.get('player_id')}")

print("\n=== ROSTERS MAPPING ===")
rosters_url = f'https://api.sleeper.app/v1/league/{league_id}/rosters'
rosters = requests.get(rosters_url).json()
roster_to_owner = {}
for roster in rosters:
    roster_to_owner[roster['roster_id']] = roster.get('owner_id')
print("Roster to Owner mapping:")
for rid, oid in roster_to_owner.items():
    print(f"  Roster {rid}: Owner {oid}")

print("\n=== USERS MAPPING ===")
users_url = f'https://api.sleeper.app/v1/league/{league_id}/users'
users = requests.get(users_url).json()
owner_to_team = {}
for user in users:
    owner_to_team[user['user_id']] = user['display_name']
print("Owner to Team mapping:")
for oid, team in owner_to_team.items():
    print(f"  Owner {oid}: {team}")

print("\n=== CHECKING PROBLEM ROSTERS ===")
problem_rosters = set()
for overall_pick in problem_picks:
    pick = next((p for p in api_picks if p['pick_no'] == overall_pick), None)
    if pick:
        problem_rosters.add(pick['roster_id'])

for roster_id in problem_rosters:
    owner_id = roster_to_owner.get(roster_id)
    team_name = owner_to_team.get(owner_id) if owner_id else None
    print(f"  Roster {roster_id}: Owner {owner_id} -> Team {team_name}")

print("\n=== DRAFT SERVICE PROCESSING ===")
try:
    from client import SleeperAPI
    client = SleeperAPI()
    picks = client.draft_service.get_draft_picks(draft_id)
    print(f"Draft service returned {len(picks)} picks")
    
    print("\nChecking for problem picks in draft service output:")
    for overall_pick in problem_picks:
        found = False
        for pick in picks:
            if pick['overall_pick'] == overall_pick:
                print(f"  #{overall_pick}: Found - {pick['player_name']} ({pick['team']})")
                found = True
                break
        if not found:
            print(f"  #{overall_pick}: MISSING from draft service")
            
except Exception as e:
    print(f"Error with draft service: {e}")