#!/usr/bin/env python3
"""
Fix the incorrect June trades
"""

def fix_june_trades():
    # Read current index.html
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Replace Justin Jefferson/Josh Reynolds trade with Xavier Restrepo/Aaron Rodgers
    # Find the incorrect trade
    incorrect_trade_start = content.find('<div class="trade-date">2025-06-11 11:33 PM</div>')
    if incorrect_trade_start == -1:
        print("ERROR: Could not find June 11 trade")
        return
    
    # Find the end of this trade
    trade_end = content.find('</div>\n                    </div>\n                    <div class="trade-item">', incorrect_trade_start)
    if trade_end == -1:
        # Must be the last trade
        trade_end = content.find('</div>\n                    </div>\n                </div>', incorrect_trade_start)
    
    # Replace with correct trade
    correct_trade = '''<div class="trade-date">2025-06-11 11:33 PM</div>
                        <div class="trade-summary">
                            <strong>ShadyCommish88 ↔ lamjohnson56</strong>
                            <span style="color: #666; margin-left: 20px;">
                                2 players, 1 picks
                            </span>
                        </div>
                        <div class="trade-teams">
                            <div class="team-side">
                                <h4>ShadyCommish88</h4>
                                <div style="color: #66ff66; margin: 5px 0;">Receives:</div>
                                <ul class="asset-list">
                                    <li class="player-item" style="display: flex; align-items: center; gap: 8px; padding: 5px 0;"><img src="https://sleepercdn.com/content/nfl/players/thumb/12520.jpg" style="width: 24px; height: 24px; border-radius: 50%; object-fit: cover;" onerror="this.outerHTML='<span style=&quot;color: #66ff66;&quot;>🏈</span>'" alt="Xavier Restrepo"><span>XAVIER RESTREPO</span></li><li class="pick-item">📋 lamjohnson56's 2026 Round 4 pick</li>
                                </ul>
                            </div>
                            
                            <div class="team-side">
                                <h4>lamjohnson56</h4>
                                <div style="color: #66ff66; margin: 5px 0;">Receives:</div>
                                <ul class="asset-list">
                                    <li class="player-item" style="display: flex; align-items: center; gap: 8px; padding: 5px 0;"><img src="https://sleepercdn.com/content/nfl/players/thumb/96.jpg" style="width: 24px; height: 24px; border-radius: 50%; object-fit: cover;" onerror="this.outerHTML='<span style=&quot;color: #66ff66;&quot;>🏈</span>'" alt="Aaron Rodgers"><span>AARON RODGERS</span></li>
                                </ul>
                            </div>
                        </div>
                        <div class="trade-grade-container">
                            <div style="margin-bottom: 8px; color: #e0e0e0; font-weight: 600;">👤 Your Trade Grade:</div>
                            <input type="range" min="0" max="100" value="50" class="trade-grade-slider" 
                                   id="trade-grade-restrepo" onchange="updateTradeGrade('restrepo', this.value)">
                            <div class="trade-grade-labels">
                                <span>ShadyCommish88 Won</span>
                                <span>Even</span>
                                <span>lamjohnson56 Won</span>
                            </div>
                            <div class="trade-grade-result" id="trade-result-restrepo">
                                <span style="color: #999999;">Move slider to grade</span>
                            </div>
                        </div>'''
    
    # Replace the trade
    trade_start = incorrect_trade_start
    new_content = content[:trade_start] + correct_trade + content[trade_end:]
    
    # Fix 2: Add ownership to the 2026 Round 3 picks in the Travis Etienne trade
    # The picks should specify whose picks they are
    new_content = new_content.replace(
        '<li class="pick-item">📋 2026 Round 3 pick</li><li class="pick-item">📋 2026 Round 3 pick</li>',
        '<li class="pick-item">📋 lamjohnson56\'s 2026 Round 3 pick</li><li class="pick-item">📋 emanueljd3\'s 2026 Round 3 pick</li>'
    )
    
    # Write back
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Fixed June 11 trade: Xavier Restrepo + pick for Aaron Rodgers")
    print("✅ Fixed missing pick ownership in Travis Etienne trade")
    print("✅ Removed fake Justin Jefferson trade")

if __name__ == "__main__":
    fix_june_trades()