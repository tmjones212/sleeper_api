#!/usr/bin/env python3
import shutil
from datetime import datetime

# First, make a backup of your current index.html
backup_name = f'../index_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
shutil.copy('../index.html', backup_name)
print(f"Created backup: {backup_name}")

# Now run the update
from client import SleeperAPI
from trade_visualization_service import LeagueVisualizationService

league_id = "1181025001438806016"
print(f"Regenerating index.html for league {league_id}...")

# Initialize and generate
client = SleeperAPI(league_id)
service = LeagueVisualizationService(client)

# Generate fresh HTML
html_content = service.generate_league_visualization_html(league_id)
with open('../index_new.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Generated new HTML as index_new.html")
print("Your original index.html is unchanged")
print("Your backup is at:", backup_name)
print("\nTo use the new version: mv index_new.html index.html")
print("To restore backup: mv", backup_name, "index.html")