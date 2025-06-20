#!/usr/bin/env python3
import re

print("Updating trades while preserving sliders...")

# Read the backup (with sliders but old trades)
with open('../index_backup_20250619_165401.html', 'r', encoding='utf-8') as f:
    html_with_sliders = f.read()

# Read the new HTML (with updated trades but no sliders)
with open('../index_new.html', 'r', encoding='utf-8') as f:
    html_with_new_trades = f.read()

# Extract the networkData from the new file
network_pattern = r'const networkData = ({.*?});'
new_network_match = re.search(network_pattern, html_with_new_trades, re.DOTALL)

if new_network_match:
    new_network_data = new_network_match.group(1)
    print("Extracted new trade data")
    
    # Replace the networkData in the file with sliders
    old_network_match = re.search(network_pattern, html_with_sliders, re.DOTALL)
    if old_network_match:
        updated_html = html_with_sliders.replace(old_network_match.group(1), new_network_data)
        print("Replaced trade data")
        
        # Also extract and update the timeline data
        timeline_pattern = r'const timelineData = (\[.*?\]);'
        new_timeline_match = re.search(timeline_pattern, html_with_new_trades, re.DOTALL)
        old_timeline_match = re.search(timeline_pattern, html_with_sliders, re.DOTALL)
        
        if new_timeline_match and old_timeline_match:
            updated_html = updated_html.replace(old_timeline_match.group(1), new_timeline_match.group(1))
            print("Updated timeline data")
        
        # Extract and update most traded players
        players_pattern = r'const mostTradedPlayers = (\[.*?\]);'
        new_players_match = re.search(players_pattern, html_with_new_trades, re.DOTALL)
        old_players_match = re.search(players_pattern, html_with_sliders, re.DOTALL)
        
        if new_players_match and old_players_match:
            updated_html = updated_html.replace(old_players_match.group(1), new_players_match.group(1))
            print("Updated most traded players")
        
        # Extract and update trade matrix
        matrix_pattern = r'const tradeMatrix = ({.*?});'
        new_matrix_match = re.search(matrix_pattern, html_with_new_trades, re.DOTALL)
        old_matrix_match = re.search(matrix_pattern, html_with_sliders, re.DOTALL)
        
        if new_matrix_match and old_matrix_match:
            updated_html = updated_html.replace(old_matrix_match.group(1), new_matrix_match.group(1))
            print("Updated trade matrix")
        
        # Save the result
        with open('../index.html', 'w', encoding='utf-8') as f:
            f.write(updated_html)
        
        print("\nSuccessfully updated trades while preserving all sliders!")
        print("Your original is backed up as index_backup_20250619_165401.html")
    else:
        print("ERROR: Could not find networkData in backup file")
else:
    print("ERROR: Could not find networkData in new file")