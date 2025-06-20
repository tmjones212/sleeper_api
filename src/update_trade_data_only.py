#!/usr/bin/env python3
import json
import re
from client import SleeperAPI
from trade_visualization_service import LeagueVisualizationService

# 2025 league ID
league_id = "1181025001438806016"
print(f"Getting fresh trade data for league {league_id}...")

# Initialize client and service
client = SleeperAPI(league_id)
service = LeagueVisualizationService(client)

# Get the network data
network_data = service.get_trade_network_data(league_id)

# Convert tuple keys to strings for JSON serialization (same as in generate_league_visualization_html)
network_data_serializable = {
    'nodes': network_data['nodes'],
    'edges': {str(k): v for k, v in network_data['edges'].items()},
    'timeline': network_data['timeline'],
    'most_active_traders': network_data['most_active_traders'],
    'biggest_trades': network_data['biggest_trades']
}

# Convert to JSON string
network_data_json = json.dumps(network_data_serializable)

# Read the index.html file
with open('../index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Find and replace the networkData line
# Using regex to match the entire line containing "const networkData ="
pattern = r'(\s*const networkData = ).*?;'
replacement = r'\1' + network_data_json + ';'

# Replace the networkData
updated_html = re.sub(pattern, replacement, html_content, count=1, flags=re.DOTALL)

# Write back to file
with open('../index.html', 'w', encoding='utf-8') as f:
    f.write(updated_html)

print("Successfully updated ONLY the trade data in index.html!")
print("Your sliders and other customizations are preserved.")