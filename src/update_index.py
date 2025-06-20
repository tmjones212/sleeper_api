#!/usr/bin/env python3
from client import SleeperAPI
from trade_visualization_service import LeagueVisualizationService

# 2025 league ID
league_id = "1181025001438806016"
print(f"Regenerating index.html with updated trades for league {league_id}...")

# Initialize client and service
client = SleeperAPI(league_id)
service = LeagueVisualizationService(client)

# Generate and save as index.html
html_content = service.generate_league_visualization_html(league_id)
with open('../index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("index.html has been updated with the latest trades!")