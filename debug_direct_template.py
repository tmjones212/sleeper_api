#!/usr/bin/env python3

import sys
sys.path.append('./src')

from trade_visualization_service import LeagueVisualizationService
from client import SleeperAPI
from jinja2 import Environment, FileSystemLoader
import os

# Create the visualization service
league_id = '1181025001438806016'
client = SleeperAPI(league_id)
service = LeagueVisualizationService(client)

# Get the exact same data that will be passed to the template
network_data = service.get_trade_network_data(league_id)
timeline_data = service.get_league_trade_timeline(league_id)
player_counts = service.transaction_service.get_player_trade_counts(league_id)
trade_matrix = service.get_team_trade_matrix(league_id)
draft_data = service.get_draft_data(league_id)
matchup_data = service.get_matchup_data(league_id)

# Convert tuple keys to strings for JSON serialization (same as in service)
network_data_serializable = {
    'nodes': network_data['nodes'],
    'edges': {str(k): v for k, v in network_data['edges'].items()},
    'timeline': network_data['timeline'],
    'most_active_traders': network_data['most_active_traders'],
    'biggest_trades': network_data['biggest_trades']
}

# Get most traded players (same as in service)
most_traded_players = []
for player_name, trade_count in sorted(player_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
    player_id = service.player_service.get_player_id_by_name(player_name)
    most_traded_players.append({
        'name': player_name,
        'trade_count': trade_count,
        'player_id': player_id,
        'image_url': service.player_service.get_player_image_url(player_id) if player_id else None
    })

# Create the exact template data that will be used
template_data = {
    'league_id': league_id,
    'network_data': network_data_serializable,
    'timeline_data': timeline_data,
    'most_traded_players': most_traded_players,
    'trade_matrix': trade_matrix,
    'draft_data': draft_data,
    'matchup_data': matchup_data,
    'visualization_type': 'all',
    'generated_at': '2025-06-20 DEBUG'
}

# Find our target trade
target_date = "2025-06-12 08:21 PM"
target_trade = None

for trade in template_data['timeline_data']['trades']:
    if trade['date'] == target_date:
        target_trade = trade
        break

if target_trade:
    print("=== TEMPLATE DATA FOR TARGET TRADE ===")
    print(f"Date: {target_trade['date']}")
    print(f"Teams: {target_trade['teams_involved']}")
    print(f"Players: {target_trade['players_count']}")
    print(f"Picks: {target_trade['picks_count']}")
    
    print("\n=== TEAM DETAILS IN TEMPLATE DATA ===")
    for team_data in target_trade['trade_details']['teams']:
        print(f"\nTeam: {team_data['team']}")
        print(f"  Receives {len(team_data['receives']['draft_picks'])} picks:")
        for pick in team_data['receives']['draft_picks']:
            print(f"    - Round {pick['round']}, Season {pick['season']}")
            print(f"    - original_owner: '{pick.get('original_owner', 'MISSING')}'")
            print(f"    - Full pick data: {pick}")
    
    # Now test the template logic directly
    print("\n=== TESTING TEMPLATE LOGIC ===")
    for team_data in target_trade['trade_details']['teams']:
        print(f"\nTeam {team_data['team']} receives:")
        for pick in team_data['receives']['draft_picks']:
            # Simulate the template logic
            if pick.get('pick_number') and pick.get('player_name'):
                result = f"Pick #{pick['pick_number']} ({pick.get('original_owner')}'s {pick['season']} R{pick['round']}) - {pick['player_name']}"
            elif pick.get('original_owner'):
                result = f"{pick['original_owner']}'s {pick['season']} Round {pick['round']} pick"
            else:
                result = f"{pick['season']} Round {pick['round']} pick"
            print(f"  Template would render: '{result}'")

else:
    print(f"Could not find trade with date '{target_date}' in template data!")
    print("\nAvailable trades:")
    for trade in template_data['timeline_data']['trades'][:5]:
        print(f"  - {trade['date']}")