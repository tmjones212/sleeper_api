#!/usr/bin/env python3
from client import SleeperAPI
from datetime import datetime
import re

league_id = "1181025001438806016"
client = SleeperAPI(league_id)

# Get all transactions
all_transactions = []
week = 1
while True:
    try:
        transactions = client.league_service.get_league_transactions(league_id, week)
        if not transactions:
            break
        all_transactions.extend(transactions)
        week += 1
    except:
        break

# Filter for new trades after May 2, 2025
trades = [t for t in all_transactions if t.get('type') == 'trade']
trades.sort(key=lambda x: x.get('status_updated', 0), reverse=True)

may_2_2025 = datetime(2025, 5, 2, 23, 59, 59).timestamp() * 1000
new_trades = [t for t in trades if t.get('status_updated', 0) > may_2_2025]

print(f"Found {len(new_trades)} new trades to add")

# Read current HTML
with open('../index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Find the current highest trade-grade ID
grade_ids = re.findall(r'id="trade-grade-(\d+)"', html_content)
if grade_ids:
    next_id = max(int(id) for id in grade_ids) + 1
else:
    next_id = 0

print(f"Next trade ID will start at: {next_id}")

# Generate HTML for new trades
new_trade_htmls = []

for i, trade in enumerate(new_trades):
    trade_id = next_id + i
    trade_date = datetime.fromtimestamp(trade['status_updated'] / 1000)
    formatted_date = trade_date.strftime('%Y-%m-%d %I:%M %p')
    
    # Get team names
    teams = []
    if trade.get('roster_names'):
        teams = trade['roster_names']
    
    if not teams:
        continue
    
    # Count assets
    players_count = len(trade.get('adds', {}))
    picks_count = len(trade.get('draft_picks', []))
    
    # Generate the trade HTML
    trade_html = f'''                    <div class="trade-item">
                        <div class="trade-date">{formatted_date}</div>
                        <div class="trade-summary">
                            <strong>{' ↔ '.join(teams)}</strong>
                            <span style="color: #666; margin-left: 20px;">
                                {players_count} players, {picks_count} picks
                            </span>
                        </div>
                        <div class="trade-teams">'''
    
    # Add team sides (simplified for now - just show team names)
    for team in teams:
        trade_html += f'''
                            
                            <div class="team-side">
                                <h4>{team}</h4>
                                <ul class="asset-list">
                                    <li class="player-item">Trade details available in data</li>
                                </ul>
                            </div>'''
    
    trade_html += f'''
                            
                        </div>
                        <div class="trade-grade-container">
                            <div style="margin-bottom: 8px; color: #e0e0e0; font-weight: 600;">👤 Your Trade Grade:</div>
                            <input type="range" min="0" max="100" value="50" class="trade-grade-slider" 
                                   id="trade-grade-{trade_id}" onchange="updateTradeGrade({trade_id}, this.value)">
                            <div class="trade-grade-labels">
                                <span>{teams[0]} Won</span>
                                <span>Even</span>
                                <span>{teams[-1]} Won</span>
                            </div>
                            <div class="trade-grade-result" id="trade-result-{trade_id}">
                                <span style="color: #999999;">Move slider to grade</span>
                            </div>
                        </div>
                    </div>

'''
    
    new_trade_htmls.append(trade_html)

# Find where to insert the new trades (right after the timeline-container div starts)
insert_pattern = r'(<div class="timeline-container">\s*)'
match = re.search(insert_pattern, html_content)

if match:
    insert_point = match.end()
    # Insert all new trades at the beginning
    new_trades_html = ''.join(new_trade_htmls)
    updated_html = html_content[:insert_point] + '\n' + new_trades_html + html_content[insert_point:]
    
    # Write back to file
    with open('../index.html', 'w', encoding='utf-8') as f:
        f.write(updated_html)
    
    print(f"Successfully added {len(new_trades)} new trades with sliders!")
else:
    print("ERROR: Could not find insertion point in HTML")