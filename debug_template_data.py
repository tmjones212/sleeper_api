#!/usr/bin/env python3

import sys
sys.path.append('./src')

from trade_visualization_service import LeagueVisualizationService
from client import SleeperAPI
import json

# Create the visualization service
league_id = '1181025001438806016'
client = SleeperAPI(league_id)
service = LeagueVisualizationService(client)

# Get timeline data (what's passed to the template)
timeline_data = service.get_league_trade_timeline(league_id)

# Find the specific problematic trade
target_date = "2025-06-12 08:21 PM"
target_trade = None

for trade in timeline_data['trades']:
    if trade['date'] == target_date:
        target_trade = trade
        break

if target_trade:
    print("Found the problematic trade in timeline data:")
    print(f"Date: {target_trade['date']}")
    print(f"Teams: {target_trade['teams_involved']}")
    print(f"Players count: {target_trade['players_count']}")
    print(f"Picks count: {target_trade['picks_count']}")
    
    print("\nTrade details structure:")
    for team_info in target_trade['trade_details']['teams']:
        print(f"\nTeam: {team_info['team']}")
        
        print(f"  Receives {len(team_info['receives']['draft_picks'])} picks:")
        for pick in team_info['receives']['draft_picks']:
            print(f"    Pick: {pick}")
            print(f"    original_owner: '{pick.get('original_owner', 'NOT SET')}'")
        
        print(f"  Gives {len(team_info['gives']['draft_picks'])} picks:")
        for pick in team_info['gives']['draft_picks']:
            print(f"    Pick: {pick}")
            print(f"    original_owner: '{pick.get('original_owner', 'NOT SET')}'")
else:
    print(f"Could not find trade with date '{target_date}'")
    print("Available trade dates:")
    for trade in timeline_data['trades'][:5]:
        print(f"  - {trade['date']}")