#!/usr/bin/env python3
from client import SleeperAPI
from trade_visualization_service import LeagueVisualizationService

# League IDs
leagues = {
    "2025": "1181025001438806016",
    "2024": "1048308938824937472", 
    "2023": "916445745966915584"
}

# Generate for 2025 season (current)
league_id = leagues["2025"]
print(f"Generating trade visualization for {league_id}...")

# Initialize client and service
client = SleeperAPI(league_id)
service = LeagueVisualizationService(client)

# Generate and save the HTML file
output_path = f"../trade_visualization_league_{league_id}_updated.html"
saved_path = service.save_league_visualization(league_id, output_path)
print(f"Trade visualization saved to: {saved_path}")

# Also update the index.html to be the latest version
print("Creating updated index.html...")
html_content = service.generate_league_visualization_html(league_id)
with open('../index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)
print("index.html updated successfully!")