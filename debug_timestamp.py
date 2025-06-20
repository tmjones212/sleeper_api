#!/usr/bin/env python3

import sys
sys.path.append('./src')

from trade_visualization_service import LeagueVisualizationService
from client import SleeperAPI
from datetime import datetime

# Create the visualization service
league_id = '1181025001438806016'
client = SleeperAPI(league_id)
service = LeagueVisualizationService(client)

# Get timeline data 
timeline_data = service.get_league_trade_timeline(league_id)

# Find trades with the target date
target_date = "2025-06-12 08:21 PM"
matching_trades = []

for trade in timeline_data['trades']:
    if target_date in trade['date']:
        matching_trades.append(trade)

print(f"Found {len(matching_trades)} trades matching '{target_date}':")

for i, trade in enumerate(matching_trades):
    print(f"\nTrade {i+1}:")
    print(f"  Date: {trade['date']}")
    print(f"  Timestamp: {trade['timestamp']}")
    print(f"  Teams: {trade['teams_involved']}")
    print(f"  Players: {trade['players_count']}")
    print(f"  Picks: {trade['picks_count']}")
    
    # Convert timestamp to datetime for verification
    try:
        trade_datetime = datetime.fromtimestamp(trade['timestamp'] / 1000)
        print(f"  Datetime: {trade_datetime}")
    except:
        print(f"  Datetime: Could not convert timestamp")
    
    # Show the trade structure
    print(f"  Teams in trade details: {len(trade['trade_details']['teams'])}")
    for team_data in trade['trade_details']['teams']:
        receives_picks = len(team_data['receives']['draft_picks'])
        gives_picks = len(team_data['gives']['draft_picks'])
        print(f"    {team_data['team']}: receives {receives_picks} picks, gives {gives_picks} picks")