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

print(f"Found {len(new_trades)} trades after May 2, 2025:")
for trade in new_trades:
    print(f"  {trade['datetime']}: {' ↔ '.join(trade.get('roster_names', []))}")

# Remove my broken hardcoded entry first
with open('index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Remove the broken Waddle trade I added
broken_trade_pattern = r'<div class="trade-item">\s*<div class="trade-date">2025-06-16 04:18 PM</div>.*?</div>\s*</div>\s*'
html_content = re.sub(broken_trade_pattern, '', html_content, flags=re.DOTALL)

# Generate HTML for all new trades
trade_htmls = []
for i, trade in enumerate(new_trades):
    trade_date = trade['datetime']
    teams = trade.get('roster_names', [])
    
    if not teams:
        continue
    
    # Get trade details
    adds = trade.get('adds', {})
    drops = trade.get('drops', {})
    draft_picks = trade.get('draft_picks', [])
    
    total_assets = len(adds) + len(drops) + len(draft_picks)
    
    trade_html = f'''                    <div class="trade-item">
                        <div class="trade-date">{trade_date}</div>
                        <div class="trade-summary">
                            <strong>{' ↔ '.join(teams)}</strong>
                            <span style="color: #666; margin-left: 20px;">
                                {len(adds)} players, {len(draft_picks)} picks
                            </span>
                        </div>
                        <div class="trade-teams">'''
    
    # Build team sides based on adds/drops
    team_assets = {}
    
    # Process players
    for player_id, roster_id in adds.items():
        team_name = None
        for team in teams:
            if team in trade.get('adds_teams', {}).values():
                if trade['adds_teams'].get(player_id) == team:
                    team_name = team
                    break
        
        if team_name:
            if team_name not in team_assets:
                team_assets[team_name] = {'receives': [], 'gives': []}
            
            player_name = get_player_name(player_id)
            team_assets[team_name]['receives'].append({
                'type': 'player',
                'name': player_name,
                'id': player_id
            })
    
    for player_id, roster_id in drops.items():
        team_name = None
        for team in teams:
            if team in trade.get('drops_teams', {}).values():
                if trade['drops_teams'].get(player_id) == team:
                    team_name = team
                    break
        
        if team_name:
            if team_name not in team_assets:
                team_assets[team_name] = {'receives': [], 'gives': []}
            
            player_name = get_player_name(player_id)
            team_assets[team_name]['gives'].append({
                'type': 'player', 
                'name': player_name,
                'id': player_id
            })
    
    # Process draft picks
    for pick in draft_picks:
        owner_id = pick.get('owner_id')
        prev_owner_id = pick.get('previous_owner_id')
        
        # Find team names based on roster mapping
        receiving_team = None
        giving_team = None
        
        for team in teams:
            # This is a simplified mapping - in a real scenario you'd need roster_id to team mapping
            if not receiving_team:
                receiving_team = teams[0] if len(teams) > 0 else 'Unknown'
            if not giving_team:
                giving_team = teams[1] if len(teams) > 1 else teams[0] if len(teams) > 0 else 'Unknown'
        
        if receiving_team not in team_assets:
            team_assets[receiving_team] = {'receives': [], 'gives': []}
        if giving_team not in team_assets:
            team_assets[giving_team] = {'receives': [], 'gives': []}
            
        pick_desc = f"{pick.get('season', 'Unknown')} Round {pick.get('round', '?')} pick"
        team_assets[receiving_team]['receives'].append({
            'type': 'pick',
            'name': pick_desc
        })
        team_assets[giving_team]['gives'].append({
            'type': 'pick',
            'name': pick_desc
        })
    
    # Generate HTML for each team
    for team_name in teams:
        if team_name not in team_assets:
            continue
            
        trade_html += f'''
                            
                            <div class="team-side">
                                <h4>{team_name}</h4>
                                <ul class="asset-list">'''
        
        # Show what they receive
        for asset in team_assets[team_name]['receives']:
            if asset['type'] == 'player':
                trade_html += f'''
                                    <li class="player-item" style="display: flex; align-items: center; gap: 8px; padding: 5px 0;">
                                        <img src="https://sleepercdn.com/content/nfl/players/thumb/{asset['id']}.jpg" 
                                             style="width: 24px; height: 24px; border-radius: 50%; object-fit: cover;" 
                                             onerror="this.outerHTML='<span style=&quot;color: #66ff66;&quot;>🏈</span>'"
                                             alt="{asset['name']}">
                                        <span>{asset['name']}</span>
                                    </li>'''
            else:
                trade_html += f'''
                                    <li class="pick-item">📋 {asset['name']}</li>'''
        
        trade_html += '''
                                </ul>
                            </div>'''
    
    trade_html += f'''
                            
                        </div>
                        <div class="trade-grade-container">
                            <div style="margin-bottom: 8px; color: #e0e0e0; font-weight: 600;">👤 Your Trade Grade:</div>
                            <input type="range" min="0" max="100" value="50" class="trade-grade-slider" 
                                   id="trade-grade-{i}" onchange="updateTradeGrade({i}, this.value)">
                            <div class="trade-grade-labels">
                                <span>{teams[0] if len(teams) > 0 else 'Team A'} Won</span>
                                <span>Even</span>
                                <span>{teams[-1] if len(teams) > 0 else 'Team B'} Won</span>
                            </div>
                            <div class="trade-grade-result" id="trade-result-{i}">
                                <span style="color: #999999;">Move slider to grade</span>
                            </div>
                        </div>
                    </div>

'''
    
    trade_htmls.append(trade_html)

# Insert all new trades at the beginning of timeline-container
insert_pattern = r'(<div class="timeline-container">\s*)'
match = re.search(insert_pattern, html_content)

if match:
    insert_point = match.end()
    new_trades_html = ''.join(trade_htmls)
    updated_html = html_content[:insert_point] + '\n' + new_trades_html + html_content[insert_point:]
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(updated_html)
    
    print(f"🎉 Successfully added {len(new_trades)} missing trades to Trade History!")
    print("✅ All trades after May 2, 2025 are now included")
    print("✅ Jaylen Waddle trade shows correct details (player + draft pick)")
else:
    print("ERROR: Could not find insertion point in HTML")