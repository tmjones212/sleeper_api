#!/usr/bin/env python3

import sys
sys.path.append('./src')

from trade_visualization_service import LeagueVisualizationService
from client import SleeperAPI

# Create the visualization service
league_id = '1181025001438806016'
client = SleeperAPI(league_id)
service = LeagueVisualizationService(client)

print("Generating HTML content...")
html_content = service.generate_league_visualization_html(league_id)

# Check if our target trade's picks are correctly rendered in the generated HTML
target_search_1 = "lamjohnson56's 2026 Round 4 pick"
target_search_2 = "lamjohnson56's 2027 Round 3 pick"
generic_search_1 = "2026 Round 4 pick"
generic_search_2 = "2027 Round 3 pick"

print(f"\nSearching in generated HTML...")
print(f"  '{target_search_1}' found: {target_search_1 in html_content}")
print(f"  '{target_search_2}' found: {target_search_2 in html_content}")
print(f"  Generic '{generic_search_1}' found: {generic_search_1 in html_content}")
print(f"  Generic '{generic_search_2}' found: {generic_search_2 in html_content}")

# Find the specific trade section
trade_date_marker = "2025-06-12 08:21 PM"
if trade_date_marker in html_content:
    start_idx = html_content.find(trade_date_marker)
    # Find the next trade or end of section
    next_trade_start = html_content.find('<div class="trade-item">', start_idx + 100)
    if next_trade_start == -1:
        trade_section = html_content[start_idx:start_idx + 2000]  # Take 2000 chars
    else:
        trade_section = html_content[start_idx:next_trade_start]
    
    print(f"\n=== TRADE SECTION IN GENERATED HTML ===")
    print(trade_section[:1000])  # First 1000 chars
    
    # Check for the specific strings in this section
    print(f"\n=== PICK STRINGS IN THIS TRADE SECTION ===")
    if "Round 4 pick" in trade_section:
        start = trade_section.find("Round 4 pick") - 50
        end = trade_section.find("Round 4 pick") + 50
        print(f"Round 4 context: ...{trade_section[start:end]}...")
    
    if "Round 3 pick" in trade_section:
        start = trade_section.find("Round 3 pick") - 50
        end = trade_section.find("Round 3 pick") + 50
        print(f"Round 3 context: ...{trade_section[start:end]}...")

else:
    print(f"Trade date '{trade_date_marker}' not found in generated HTML!")

# Save a test version to compare
with open('/home/alaba/coolProjects/test_index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\nSaved test HTML to test_index.html for comparison")