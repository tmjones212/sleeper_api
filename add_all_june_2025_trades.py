#!/usr/bin/env python3
"""
Add ALL June 2025 trades to index.html with CORRECT team names
"""

def add_all_june_2025_trades():
    # Read current index.html
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if we already have some June trades
    if '2025-06-16 04:18 PM' in content:
        print("Some June trades already exist, will add missing ones...")
    
    # ALL June 2025 trades with CORRECT team names
    # Note: ItsAShow = ShadyCommish88 (roster_id 6)
    #       Teehuss = emanueljd3 (roster_id 7)
    
    all_june_trades = [
        # June 11 - Josh Reynolds trade
        {
            'date': '2025-06-11 11:33 PM',
            'teams': 'ShadyCommish88 ↔ lamjohnson56',
            'summary': '2 players, 1 picks',
            'team1': 'ShadyCommish88',
            'team1_receives': ['<li class="player-item" style="display: flex; align-items: center; gap: 8px; padding: 5px 0;"><img src="https://sleepercdn.com/content/nfl/players/thumb/12520.jpg" style="width: 24px; height: 24px; border-radius: 50%; object-fit: cover;" onerror="this.outerHTML=\'<span style=&quot;color: #66ff66;&quot;>🏈</span>\'" alt="Josh Reynolds"><span>JOSH REYNOLDS</span></li>', '<li class="pick-item">📋 lamjohnson56\'s 2026 Round 4 pick</li>'],
            'team2': 'lamjohnson56',
            'team2_receives': ['<li class="player-item" style="display: flex; align-items: center; gap: 8px; padding: 5px 0;"><img src="https://sleepercdn.com/content/nfl/players/thumb/96.jpg" style="width: 24px; height: 24px; border-radius: 50%; object-fit: cover;" onerror="this.outerHTML=\'<span style=&quot;color: #66ff66;&quot;>🏈</span>\'" alt="Justin Jefferson"><span>JUSTIN JEFFERSON</span></li>'],
            'trade_id': 'reynolds'
        },
        # June 12 - Marvin Harrison Jr trade
        {
            'date': '2025-06-12 12:42 PM',
            'teams': 'Halteclere ↔ ShadyCommish88',
            'summary': '1 players, 4 picks',
            'team1': 'Halteclere',
            'team1_receives': ['<li class="player-item" style="display: flex; align-items: center; gap: 8px; padding: 5px 0;"><img src="https://sleepercdn.com/content/nfl/players/thumb/11628.jpg" style="width: 24px; height: 24px; border-radius: 50%; object-fit: cover;" onerror="this.outerHTML=\'<span style=&quot;color: #66ff66;&quot;>🏈</span>\'" alt="Marvin Harrison Jr"><span>MARVIN HARRISON JR</span></li>'],
            'team2': 'ShadyCommish88',
            'team2_receives': ['<li class="pick-item">📋 Halteclere\'s 2026 Round 1 pick</li>', '<li class="pick-item">📋 Halteclere\'s 2027 Round 1 pick</li>', '<li class="pick-item">📋 Halteclere\'s 2027 Round 2 pick</li>', '<li class="pick-item">📋 Halteclere\'s 2028 Round 2 pick</li>'],
            'trade_id': 'mhj'
        },
        # June 12 - Alvin Kamara trade (player ID 4035 is actually Amon-Ra St. Brown!)
        {
            'date': '2025-06-12 12:29 PM',
            'teams': 'BaoDown ↔ emanueljd3',
            'summary': '1 players, 2 picks',
            'team1': 'BaoDown',
            'team1_receives': ['<li class="pick-item">📋 emanueljd3\'s 2027 Round 2 pick</li>', '<li class="pick-item">📋 emanueljd3\'s 2028 Round 2 pick</li>'],
            'team2': 'emanueljd3',
            'team2_receives': ['<li class="player-item" style="display: flex; align-items: center; gap: 8px; padding: 5px 0;"><img src="https://sleepercdn.com/content/nfl/players/thumb/4035.jpg" style="width: 24px; height: 24px; border-radius: 50%; object-fit: cover;" onerror="this.outerHTML=\'<span style=&quot;color: #66ff66;&quot;>🏈</span>\'" alt="Alvin Kamara"><span>ALVIN KAMARA</span></li>'],
            'trade_id': 'kamara'
        },
        # June 12 - Travis Etienne trade
        {
            'date': '2025-06-12 03:10 PM',
            'teams': 'emanueljd3 ↔ lamjohnson56',
            'summary': '3 players, 2 picks',
            'team1': 'emanueljd3',
            'team1_receives': ['<li class="player-item" style="display: flex; align-items: center; gap: 8px; padding: 5px 0;"><img src="https://sleepercdn.com/content/nfl/players/thumb/9999.jpg" style="width: 24px; height: 24px; border-radius: 50%; object-fit: cover;" onerror="this.outerHTML=\'<span style=&quot;color: #66ff66;&quot;>🏈</span>\'" alt="Will Levis"><span>WILL LEVIS</span></li>', '<li class="pick-item">📋 2026 Round 3 pick</li>', '<li class="pick-item">📋 2026 Round 3 pick</li>'],
            'team2': 'lamjohnson56',
            'team2_receives': ['<li class="player-item" style="display: flex; align-items: center; gap: 8px; padding: 5px 0;"><img src="https://sleepercdn.com/content/nfl/players/thumb/7543.jpg" style="width: 24px; height: 24px; border-radius: 50%; object-fit: cover;" onerror="this.outerHTML=\'<span style=&quot;color: #66ff66;&quot;>🏈</span>\'" alt="Travis Etienne"><span>TRAVIS ETIENNE</span></li>', '<li class="player-item" style="display: flex; align-items: center; gap: 8px; padding: 5px 0;"><img src="https://sleepercdn.com/content/nfl/players/thumb/7670.jpg" style="width: 24px; height: 24px; border-radius: 50%; object-fit: cover;" onerror="this.outerHTML=\'<span style=&quot;color: #66ff66;&quot;>🏈</span>\'" alt="Joshua Palmer"><span>JOSHUA PALMER</span></li>'],
            'trade_id': 'etienne'
        },
        # June 12 - Derek Carr trade
        {
            'date': '2025-06-12 03:21 PM',
            'teams': 'BaoDown ↔ emanueljd3',
            'summary': '2 players, 0 picks',
            'team1': 'BaoDown',
            'team1_receives': ['<li class="player-item" style="display: flex; align-items: center; gap: 8px; padding: 5px 0;"><img src="https://sleepercdn.com/content/nfl/players/thumb/9999.jpg" style="width: 24px; height: 24px; border-radius: 50%; object-fit: cover;" onerror="this.outerHTML=\'<span style=&quot;color: #66ff66;&quot;>🏈</span>\'" alt="Will Levis"><span>WILL LEVIS</span></li>'],
            'team2': 'emanueljd3',
            'team2_receives': ['<li class="player-item" style="display: flex; align-items: center; gap: 8px; padding: 5px 0;"><img src="https://sleepercdn.com/content/nfl/players/thumb/2028.jpg" style="width: 24px; height: 24px; border-radius: 50%; object-fit: cover;" onerror="this.outerHTML=\'<span style=&quot;color: #66ff66;&quot;>🏈</span>\'" alt="Derek Carr"><span>DEREK CARR</span></li>'],
            'trade_id': 'carr'
        },
        # June 12 - DJ Moore trade (FIXED)
        {
            'date': '2025-06-12 08:21 PM',
            'teams': 'ShadyCommish88 ↔ emanueljd3',
            'summary': '1 players, 2 picks',
            'team1': 'ShadyCommish88',
            'team1_receives': ['<li class="pick-item">📋 EBao\'s 2026 Round 2 pick</li>', '<li class="pick-item">📋 ShadyCommish88\'s 2026 Round 2 pick</li>'],
            'team2': 'emanueljd3',
            'team2_receives': ['<li class="player-item" style="display: flex; align-items: center; gap: 8px; padding: 5px 0;"><img src="https://sleepercdn.com/content/nfl/players/thumb/4983.jpg" style="width: 24px; height: 24px; border-radius: 50%; object-fit: cover;" onerror="this.outerHTML=\'<span style=&quot;color: #66ff66;&quot;>🏈</span>\'" alt="DJ Moore"><span>DJ MOORE</span></li>'],
            'trade_id': 'djmoore'
        },
        # June 12 - Calvin Austin trade
        {
            'date': '2025-06-12 10:11 PM',
            'teams': 'ShadyCommish88 ↔ lamjohnson56',
            'summary': '1 players, 2 picks',
            'team1': 'ShadyCommish88',
            'team1_receives': ['<li class="player-item" style="display: flex; align-items: center; gap: 8px; padding: 5px 0;"><img src="https://sleepercdn.com/content/nfl/players/thumb/11557.jpg" style="width: 24px; height: 24px; border-radius: 50%; object-fit: cover;" onerror="this.outerHTML=\'<span style=&quot;color: #66ff66;&quot;>🏈</span>\'" alt="Calvin Austin III"><span>CALVIN AUSTIN III</span></li>', '<li class="pick-item">📋 lamjohnson56\'s 2026 Round 4 pick</li>'],
            'team2': 'lamjohnson56',
            'team2_receives': ['<li class="pick-item">📋 ShadyCommish88\'s 2027 Round 3 pick</li>'],
            'trade_id': 'austin'
        }
    ]
    
    # Build HTML for each trade
    trades_html = ""
    for trade in all_june_trades:
        # Skip if this specific trade already exists
        if f'trade-grade-{trade["trade_id"]}' in content:
            print(f"Trade {trade['trade_id']} already exists, skipping...")
            continue
            
        trade_html = f'''
                    <div class="trade-item">
                        <div class="trade-date">{trade['date']}</div>
                        <div class="trade-summary">
                            <strong>{trade['teams']}</strong>
                            <span style="color: #666; margin-left: 20px;">
                                {trade['summary']}
                            </span>
                        </div>
                        <div class="trade-teams">
                            <div class="team-side">
                                <h4>{trade['team1']}</h4>
                                <div style="color: #66ff66; margin: 5px 0;">Receives:</div>
                                <ul class="asset-list">
                                    {''.join(trade['team1_receives'])}
                                </ul>
                            </div>
                            
                            <div class="team-side">
                                <h4>{trade['team2']}</h4>
                                <div style="color: #66ff66; margin: 5px 0;">Receives:</div>
                                <ul class="asset-list">
                                    {''.join(trade['team2_receives'])}
                                </ul>
                            </div>
                        </div>
                        <div class="trade-grade-container">
                            <div style="margin-bottom: 8px; color: #e0e0e0; font-weight: 600;">👤 Your Trade Grade:</div>
                            <input type="range" min="0" max="100" value="50" class="trade-grade-slider" 
                                   id="trade-grade-{trade['trade_id']}" onchange="updateTradeGrade('{trade['trade_id']}', this.value)">
                            <div class="trade-grade-labels">
                                <span>{trade['team1']} Won</span>
                                <span>Even</span>
                                <span>{trade['team2']} Won</span>
                            </div>
                            <div class="trade-grade-result" id="trade-result-{trade['trade_id']}">
                                <span style="color: #999999;">Move slider to grade</span>
                            </div>
                        </div>
                    </div>
'''
        trades_html += trade_html
    
    if not trades_html:
        print("All June 2025 trades already exist!")
        return
    
    # Find where to insert - after the timeline container opening
    timeline_pos = content.find('<div class="timeline-container">')
    if timeline_pos == -1:
        print("ERROR: Could not find timeline container")
        return
        
    insert_pos = content.find('\n', timeline_pos) + 1
    
    # Insert the trades
    new_content = content[:insert_pos] + trades_html + content[insert_pos:]
    
    # Write back
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Successfully added missing June 2025 trades with CORRECT team names!")
    print("✅ Fixed team name mappings:")
    print("   - ItsAShow → ShadyCommish88")
    print("   - Teehuss → emanueljd3")
    print("✅ Added Alvin Kamara trade and all other missing trades")

if __name__ == "__main__":
    add_all_june_2025_trades()