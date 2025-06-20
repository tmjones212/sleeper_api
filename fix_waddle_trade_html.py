#!/usr/bin/env python3
from datetime import datetime
import re
import json

# Load transaction data directly
with open('src/data/league_1181025001438806016_transactions.json', 'r') as f:
    all_transactions = json.load(f)

# Load player data
with open('src/data/players.json', 'r') as f:
    players = json.load(f)

def get_player_name(player_id):
    if player_id in players:
        return players[player_id]['name']
    return f"Unknown Player {player_id}"

# Find the specific Waddle trade (June 16, 4:18 PM)
waddle_trade = None
for t in all_transactions:
    if t.get('type') == 'trade' and t.get('datetime') == '2025-06-16 04:18 PM':
        waddle_trade = t
        break

if not waddle_trade:
    print("ERROR: Could not find Waddle trade!")
    exit(1)

print(f"Found Waddle trade: {waddle_trade['datetime']}")
print(f"Teams: {waddle_trade.get('roster_names', [])}")
print(f"Adds: {waddle_trade.get('adds', {})}")
print(f"Drops: {waddle_trade.get('drops', {})}")

# Generate proper HTML for the Waddle trade
teams = waddle_trade.get('roster_names', [])
adds = waddle_trade.get('adds', {})
drops = waddle_trade.get('drops', {})

# Build detailed trade HTML
trade_html = f'''                    <div class="trade-item">
                        <div class="trade-date">2025-06-16 04:18 PM</div>
                        <div class="trade-summary">
                            <strong>{' ↔ '.join(teams)}</strong>
                            <span style="color: #666; margin-left: 20px;">
                                {len(adds) + len(drops)} players, 0 picks
                            </span>
                        </div>
                        <div class="trade-teams">'''

# Add Halteclere side (receives Jaylen Waddle)
trade_html += f'''
                            
                            <div class="team-side">
                                <h4>Halteclere</h4>
                                <ul class="asset-list">'''

for player_id, roster_id in adds.items():
    player_name = get_player_name(player_id)
    trade_html += f'''
                                    <li class="player-item" style="display: flex; align-items: center; gap: 8px; padding: 5px 0;">
                                        <img src="https://sleepercdn.com/content/nfl/players/thumb/{player_id}.jpg" 
                                             style="width: 24px; height: 24px; border-radius: 50%; object-fit: cover;" 
                                             onerror="this.outerHTML='<span style=&quot;color: #66ff66;&quot;>🏈</span>'"
                                             alt="{player_name}">
                                        <span>{player_name}</span>
                                    </li>'''

trade_html += '''
                                </ul>
                            </div>'''

# Add lamjohnson56 side (gives up Jaylen Waddle)  
trade_html += f'''
                            
                            <div class="team-side">
                                <h4>lamjohnson56</h4>
                                <ul class="asset-list">'''

for player_id, team in drops.items():
    player_name = get_player_name(player_id)
    trade_html += f'''
                                    <li class="player-item" style="display: flex; align-items: center; gap: 8px; padding: 5px 0;">
                                        <img src="https://sleepercdn.com/content/nfl/players/thumb/{player_id}.jpg" 
                                             style="width: 24px; height: 24px; border-radius: 50%; object-fit: cover;" 
                                             onerror="this.outerHTML='<span style=&quot;color: #66ff66;&quot;>🏈</span>'"
                                             alt="{player_name}">
                                        <span>{player_name}</span>
                                    </li>'''

trade_html += '''
                                </ul>
                            </div>
                            
                        </div>
                        <div class="trade-grade-container">
                            <div style="margin-bottom: 8px; color: #e0e0e0; font-weight: 600;">👤 Your Trade Grade:</div>
                            <input type="range" min="0" max="100" value="50" class="trade-grade-slider" 
                                   id="trade-grade-waddle" onchange="updateTradeGrade('waddle', this.value)">
                            <div class="trade-grade-labels">
                                <span>Halteclere Won</span>
                                <span>Even</span>
                                <span>lamjohnson56 Won</span>
                            </div>
                            <div class="trade-grade-result" id="trade-result-waddle">
                                <span style="color: #999999;">Move slider to grade</span>
                            </div>
                        </div>
                    </div>

'''

# Read current HTML
with open('index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Find the timeline-container and insert the Waddle trade at the very beginning
insert_pattern = r'(<div class="timeline-container">\s*)'
match = re.search(insert_pattern, html_content)

if match:
    insert_point = match.end()
    updated_html = html_content[:insert_point] + '\n' + trade_html + html_content[insert_point:]
    
    # Write back to file
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(updated_html)
    
    print("🎉 Successfully added Jaylen Waddle trade to Trade History!")
    print("✅ The trade will now appear at the top of the Trade History section")
    print("✅ Jaylen Waddle's name and image will be properly displayed")
else:
    print("ERROR: Could not find insertion point in HTML")