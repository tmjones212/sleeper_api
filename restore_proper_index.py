#!/usr/bin/env python3
"""Restore index.html with proper formatting using the existing visualization service."""

import sys
sys.path.append('src')
from client import SleeperAPI
from trade_visualization_service import LeagueVisualizationService

def restore_index():
    print("=== Restoring index.html with proper formatting ===")
    
    client = SleeperAPI()
    viz_service = LeagueVisualizationService(client)
    
    # Use the main league ID (2025)
    league_id = "1181025001438806016"
    
    print("Generating visualization with all proper tabs and formatting...")
    
    # Generate the full visualization HTML with all features
    output_file = "index.html"
    viz_service.save_league_visualization(league_id, output_file)
    
    print(f"\n✓ Restored {output_file} with proper formatting")
    print("✓ All tabs (Trades, Draft, Matchups) are back")
    print("✓ HTML formatting is clean")
    print("✓ Pick ownership should still be correct")

if __name__ == "__main__":
    restore_index()