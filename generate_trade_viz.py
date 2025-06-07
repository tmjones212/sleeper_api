#!/usr/bin/env python3

from src.client import SleeperAPI
from src.trade_visualization_service import TradeVisualizationService

# Use the main league ID from your main.py
league_id = "1181025001438806016"  # 2025

print("Initializing Sleeper API client...")
client = SleeperAPI(league_id)

print("Creating trade visualization service...")
viz_service = TradeVisualizationService(client)

print("Generating trade visualization HTML with draft data...")
output_file = viz_service.save_trade_visualization(league_id)

print(f"Trade visualization saved to: {output_file}")
print("The new HTML file now includes the draft results tab!")