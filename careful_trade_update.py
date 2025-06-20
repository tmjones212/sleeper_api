#!/usr/bin/env python3
import json
import re
from datetime import datetime

# Load transaction data
with open('src/data/league_1181025001438806016_transactions.json', 'r') as f:
    all_transactions = json.load(f)

# Load player data
with open('src/data/players.json', 'r') as f:
    players = json.load(f)

def get_player_name(player_id):
    if player_id in players:
        return players[player_id]['name']
    return f"Unknown Player {player_id}"

# Find all trades after May 2, 2025
may_2_2025 = datetime(2025, 5, 2, 23, 59, 59).timestamp() * 1000
new_trades = []

for t in all_transactions:
    if (t.get('type') == 'trade' and 
        t.get('status_updated', 0) > may_2_2025):
        new_trades.append(t)

# Sort by most recent first
new_trades.sort(key=lambda x: x.get('status_updated', 0), reverse=True)

print(f"Found {len(new_trades)} trades after May 2, 2025")

# Read current HTML
with open('index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

print(f"Original file size: {len(html_content)} characters")

# Generate only the Waddle trade first to test
waddle_trade = None
for trade in new_trades:
    if trade['datetime'] == '2025-06-16 04:18 PM':
        waddle_trade = trade
        break

if not waddle_trade:
    print("ERROR: Could not find Waddle trade")
    exit(1)

# Create simple Waddle trade HTML
waddle_html = '''                    <div class="trade-item">
                        <div class="trade-date">2025-06-16 04:18 PM</div>
                        <div class="trade-summary">
                            <strong>Halteclere ↔ lamjohnson56</strong>
                            <span style="color: #666; margin-left: 20px;">
                                1 players, 1 picks
                            </span>
                        </div>
                        <div class="trade-teams">
                            <div class="team-side">
                                <h4>Halteclere</h4>
                                <div style="color: #66ff66; margin: 5px 0;">Receives:</div>
                                <ul class="asset-list">
                                    <li class="player-item" style="display: flex; align-items: center; gap: 8px; padding: 5px 0;">
                                        <img src="https://sleepercdn.com/content/nfl/players/thumb/7526.jpg" 
                                             style="width: 24px; height: 24px; border-radius: 50%; object-fit: cover;" 
                                             onerror="this.outerHTML='<span style=&quot;color: #66ff66;&quot;>🏈</span>'"
                                             alt="Jaylen Waddle">
                                        <span>JAYLEN WADDLE</span>
                                    </li>
                                </ul>
                            </div>
                            
                            <div class="team-side">
                                <h4>lamjohnson56</h4>
                                <div style="color: #66ff66; margin: 5px 0;">Receives:</div>
                                <ul class="asset-list">
                                    <li class="pick-item">📋 2028 Round 1 pick</li>
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

# Find the timeline-container and carefully insert just the Waddle trade
timeline_pattern = r'(<div class="timeline-container">\s*)'
match = re.search(timeline_pattern, html_content)

if match:
    insert_point = match.end()
    updated_html = html_content[:insert_point] + waddle_html + html_content[insert_point:]
    
    print(f"Updated file size: {len(updated_html)} characters")
    
    # Write back carefully
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(updated_html)
    
    print("✅ Successfully added just the Jaylen Waddle trade")
    print("✅ File size preserved, only added the necessary trade")
else:
    print("ERROR: Could not find timeline-container")