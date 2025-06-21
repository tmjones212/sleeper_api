#!/usr/bin/env python3
"""
Updates the trade history in index.html to show who actually made each draft pick.
This will add indicators when the receiving team didn't make the pick themselves.
"""
import re
import sys
import os

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from client import SleeperAPI
from transaction_service import TransactionService

def update_trade_history_html(html_content, league_id):
    """Update trade history HTML to show who actually made draft picks."""
    # Initialize client and service
    client = SleeperAPI(league_id)
    service = TransactionService(client)
    
    # Get all trades with proper ownership data
    trades = service.get_trades(league_id)
    
    # Create a comprehensive mapping of pick info
    pick_details = {}
    
    for trade in trades:
        if 'team_assets' in trade:
            for team_name, assets in trade['team_assets'].items():
                for direction in ['receives', 'gives']:
                    if direction in assets:
                        for asset in assets[direction]:
                            if asset.get('type') == 'draft_pick':
                                # Create unique keys for the pick
                                if asset.get('pick_number') and asset.get('player_name'):
                                    # This pick has been used
                                    key1 = f"Pick #{asset['pick_number']}"
                                    key2 = f"{asset.get('original_owner', '')}'s {asset['season']} R{asset['round']}"
                                    
                                    # Determine who received the pick in this trade
                                    receiving_team = team_name if direction == 'receives' else None
                                    
                                    pick_details[key1] = {
                                        'player_name': asset.get('player_name'),
                                        'picking_team': asset.get('picking_team'),  # Who actually made the pick
                                        'receiving_team': receiving_team,  # Who got the pick in this trade
                                        'original_owner': asset.get('original_owner')
                                    }
                                    pick_details[key2] = pick_details[key1]
    
    # Function to enhance pick display
    def enhance_pick(match):
        full_match = match.group(0)
        pick_content = match.group(1)
        
        # Extract pick number if present
        pick_num_match = re.search(r'Pick #(\d+)', pick_content)
        if pick_num_match:
            pick_num = f"Pick #{pick_num_match.group(1)}"
            if pick_num in pick_details:
                details = pick_details[pick_num]
                picking_team = details.get('picking_team')
                receiving_team = details.get('receiving_team')
                
                # Check if the receiving team actually made the pick
                if picking_team and receiving_team and picking_team != receiving_team:
                    # The pick was traded again before being used
                    enhanced_content = pick_content + f' <span style="color: #ff9800; font-size: 0.9em;">(actually picked by {picking_team})</span>'
                    return full_match.replace(pick_content, enhanced_content)
        
        return full_match
    
    # Pattern to match pick items with draft results
    pattern = r'<li class="pick-item">📋 ([^<]+)</li>'
    
    # Replace all picks with enhanced info
    updated_html = re.sub(pattern, enhance_pick, html_content)
    
    # Count how many picks were enhanced
    enhanced_count = len(re.findall(r'\(actually picked by', updated_html))
    print(f"Enhanced {enhanced_count} draft picks with actual picking team info")
    
    # Debug: Show all picks we found details for
    print(f"\nFound details for {len(pick_details)} draft picks:")
    for key, details in list(pick_details.items())[:5]:  # Show first 5
        if 'Pick #' in key:
            print(f"  {key}: {details['player_name']} - receiving_team: {details.get('receiving_team')}, picking_team: {details.get('picking_team')}")
    
    return updated_html

def main():
    league_id = "1181025001438806016"
    
    print("Updating trade history with draft pick details...")
    
    # Read existing index.html
    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Update trade history
    updated_html = update_trade_history_html(html_content, league_id)
    
    # Write back to index.html
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(updated_html)
    
    print("Successfully updated trade history with picking team information!")
    print("Picks that were traded before being used now show '(picked by TeamName)' in orange.")

if __name__ == "__main__":
    main()