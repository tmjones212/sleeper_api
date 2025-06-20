#!/usr/bin/env python3
"""
Updates only the trade data in the existing index.html without changing the structure.
This preserves the original layout, manager rankings, and trade sliders.
"""
import re
import json
from client import SleeperAPI
from transaction_service import TransactionService

def update_trades_in_html(html_content, new_trades_data):
    """Update only the tradesData variable in the HTML."""
    # Find and replace the tradesData variable
    pattern = r'const tradesData = (\[[\s\S]*?\]);'
    
    # Convert trades data to JSON string with proper formatting
    trades_json = json.dumps(new_trades_data, indent=8)
    
    # Replace the old trades data with new
    replacement = f'const tradesData = {trades_json};'
    
    updated_html = re.sub(pattern, replacement, html_content, count=1)
    
    return updated_html

def main():
    # League ID
    league_id = "1181025001438806016"
    print(f"Updating trades for league {league_id}...")
    
    # Initialize client and service
    client = SleeperAPI(league_id)
    service = TransactionService(client)
    
    # Get updated trade data
    trades = service.get_trades(league_id)
    
    # Read existing index.html
    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Check if this is the original format (has tradesData)
    if 'const tradesData = ' not in html_content:
        print("ERROR: This index.html doesn't have the original tradesData structure!")
        print("Please restore the original index.html first.")
        return
    
    # Update only the trades data
    updated_html = update_trades_in_html(html_content, trades)
    
    # Write back to index.html
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(updated_html)
    
    print("Successfully updated trade data without changing HTML structure!")
    
    # Count trades to verify
    trade_count = len(trades)
    print(f"Total trades updated: {trade_count}")

if __name__ == "__main__":
    main()