#!/usr/bin/env python3
"""
Updates only the draft pick displays in index.html to show original ownership.
This preserves all other HTML structure and functionality.
"""
import re
from client import SleeperAPI
from transaction_service import TransactionService

def update_pick_displays(html_content, league_id):
    """Update draft pick displays to include original owner."""
    # Initialize client and service
    client = SleeperAPI(league_id)
    service = TransactionService(client)
    
    # Get all trades with proper ownership data
    trades = service.get_trades(league_id)
    
    # Create a mapping of pick identifiers to their original owners
    pick_ownership = {}
    
    for trade in trades:
        if 'team_assets' in trade:
            for team_name, assets in trade['team_assets'].items():
                for direction in ['receives', 'gives']:
                    if direction in assets:
                        for asset in assets[direction]:
                            if asset.get('type') == 'draft_pick' and asset.get('original_owner'):
                                # Create a unique key for this pick
                                key = f"{asset['season']} Round {asset['round']} pick"
                                pick_ownership[key] = asset['original_owner']
    
    # Function to replace pick text
    def replace_pick(match):
        full_match = match.group(0)
        pick_text = match.group(1)
        
        # Check if this pick already has an owner (contains "'s")
        if "'s" in pick_text:
            return full_match
        
        # Try to find the owner for this pick
        if pick_text in pick_ownership:
            owner = pick_ownership[pick_text]
            new_pick_text = f"{owner}'s {pick_text}"
            return full_match.replace(pick_text, new_pick_text)
        
        return full_match
    
    # Pattern to match pick items
    pattern = r'<li class="pick-item">📋 ([0-9]{4} Round [0-9] pick)</li>'
    
    # Replace all picks with ownership info
    updated_html = re.sub(pattern, replace_pick, html_content)
    
    # Count how many picks were updated
    original_picks = len(re.findall(pattern, html_content))
    updated_picks = len(re.findall(r"'s [0-9]{4} Round [0-9] pick", updated_html))
    
    print(f"Updated {updated_picks} out of {original_picks} draft picks with ownership info")
    
    return updated_html

def main():
    league_id = "1181025001438806016"
    
    print("Updating draft pick ownership in index.html...")
    
    # Read existing index.html
    with open('../index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Update pick displays
    updated_html = update_pick_displays(html_content, league_id)
    
    # Write back to index.html
    with open('../index.html', 'w', encoding='utf-8') as f:
        f.write(updated_html)
    
    print("Successfully updated draft pick ownership!")

if __name__ == "__main__":
    main()