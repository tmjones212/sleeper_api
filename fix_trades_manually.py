#!/usr/bin/env python3
"""
Manually fix the trade display issues:
1. Remove duplicate DJ Moore trades
2. Add missing Jaylen Waddle trade
"""
import re
from datetime import datetime

def fix_trades():
    # Read current HTML
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create backup
    import shutil
    backup_name = f'index_backup_manual_fix_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
    shutil.copy('index.html', backup_name)
    print(f"Created backup: {backup_name}")
    
    # Find the timeline container
    timeline_start = content.find('<div class="timeline-container">')
    if timeline_start == -1:
        print("ERROR: Could not find timeline container")
        return
    
    # Find where to insert the Jaylen Waddle trade (at the beginning of timeline-container)
    insert_point = timeline_start + len('<div class="timeline-container">') + 1
    
    # Add the Jaylen Waddle trade as the first trade (most recent)
    waddle_trade = '''
                    <div class="trade-item">
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
                                    <li class="pick-item">📋 Halteclere's 2028 Round 1 pick</li>
                                </ul>
                            </div>
                        </div>
                        <div class="trade-grade-container">
                            <div style="margin-bottom: 8px; color: #e0e0e0; font-weight: 600;">👤 Your Trade Grade:</div>
                            <input type="range" min="0" max="100" value="50" class="trade-grade-slider" 
                                   id="trade-grade-0" onchange="updateTradeGrade(0, this.value)">
                            <div class="trade-grade-labels">
                                <span>Halteclere Won</span>
                                <span>Even</span>
                                <span>lamjohnson56 Won</span>
                            </div>
                            <div class="trade-grade-result" id="trade-result-0">
                                <span style="color: #999999;">Move slider to grade</span>
                            </div>
                        </div>
                    </div>

'''
    
    # Insert Waddle trade at the beginning
    new_content = content[:insert_point] + waddle_trade + content[insert_point:]
    
    # Now find and fix the duplicate DJ Moore trade
    # The issue is that the 2025-06-12 02:02 PM trade shows wrong team sides
    
    # Find the problematic trade
    dj_moore_pattern = r'(<div class="trade-item">.*?2025-06-12 02:02 PM.*?</div>\s*</div>)'
    
    # Find all matches
    matches = list(re.finditer(dj_moore_pattern, new_content, re.DOTALL))
    
    if matches:
        print(f"Found {len(matches)} DJ Moore trades from 2025-06-12 02:02 PM")
        
        # Check each match to see if it has the wrong team structure
        for match in matches:
            trade_html = match.group(1)
            if 'emanueljd3 ↔ lamjohnson56' in trade_html and '<h4>ShadyCommish88</h4>' in trade_html:
                print("Found the problematic trade with wrong team names!")
                
                # Replace the team sides with correct ones
                correct_trade = '''<div class="trade-item">
                        <div class="trade-date">2025-06-12 02:02 PM</div>
                        <div class="trade-summary">
                            <strong>emanueljd3 ↔ lamjohnson56</strong>
                            <span style="color: #666; margin-left: 20px;">
                                3 players, 2 picks
                            </span>
                        </div>
                        <div class="trade-teams">
                            <div class="team-side">
                                <h4>emanueljd3</h4>
                                <div style="color: #66ff66; margin: 5px 0;">Receives:</div>
                                <ul class="asset-list">
                                    <li class="player-item" style="display: flex; align-items: center; gap: 8px; padding: 5px 0;">
                                        <img src="https://sleepercdn.com/content/nfl/players/thumb/5937.jpg" 
                                             style="width: 24px; height: 24px; border-radius: 50%; object-fit: cover;" 
                                             onerror="this.outerHTML='<span style=&quot;color: #66ff66;&quot;>🏈</span>'"
                                             alt="DIONTAE JOHNSON">
                                        <span>DIONTAE JOHNSON</span>
                                    </li>
                                    <li class="pick-item">📋 lamjohnson56's 2026 Round 1 pick</li>
                                    <li class="pick-item">📋 lamjohnson56's 2027 Round 1 pick</li>
                                </ul>
                            </div>
                            
                            <div class="team-side">
                                <h4>lamjohnson56</h4>
                                <div style="color: #66ff66; margin: 5px 0;">Receives:</div>
                                <ul class="asset-list">
                                    <li class="player-item" style="display: flex; align-items: center; gap: 8px; padding: 5px 0;">
                                        <img src="https://sleepercdn.com/content/nfl/players/thumb/4983.jpg" 
                                             style="width: 24px; height: 24px; border-radius: 50%; object-fit: cover;" 
                                             onerror="this.outerHTML='<span style=&quot;color: #66ff66;&quot;>🏈</span>'"
                                             alt="DJ MOORE">
                                        <span>DJ MOORE</span>
                                    </li>
                                    <li class="player-item" style="display: flex; align-items: center; gap: 8px; padding: 5px 0;">
                                        <img src="https://sleepercdn.com/content/nfl/players/thumb/5965.jpg" 
                                             style="width: 24px; height: 24px; border-radius: 50%; object-fit: cover;" 
                                             onerror="this.outerHTML='<span style=&quot;color: #66ff66;&quot;>🏈</span>'"
                                             alt="TREVOR SIEMIAN">
                                        <span>TREVOR SIEMIAN</span>
                                    </li>
                                    <li class="player-item" style="display: flex; align-items: center; gap: 8px; padding: 5px 0;">
                                        <img src="https://sleepercdn.com/content/nfl/players/thumb/6156.jpg" 
                                             style="width: 24px; height: 24px; border-radius: 50%; object-fit: cover;" 
                                             onerror="this.outerHTML='<span style=&quot;color: #66ff66;&quot;>🏈</span>'"
                                             alt="DANIEL JONES">
                                        <span>DANIEL JONES</span>
                                    </li>
                                </ul>
                            </div>
                        </div>
                        <div class="trade-grade-container">
                            <div style="margin-bottom: 8px; color: #e0e0e0; font-weight: 600;">👤 Your Trade Grade:</div>
                            <input type="range" min="0" max="100" value="50" class="trade-grade-slider" 
                                   id="trade-grade-5" onchange="updateTradeGrade(5, this.value)">
                            <div class="trade-grade-labels">
                                <span>emanueljd3 Won</span>
                                <span>Even</span>
                                <span>lamjohnson56 Won</span>
                            </div>
                            <div class="trade-grade-result" id="trade-result-5">
                                <span style="color: #999999;">Move slider to grade</span>
                            </div>
                        </div>
                    </div>'''
                
                new_content = new_content[:match.start()] + correct_trade + new_content[match.end():]
                break
    
    # Write the fixed content
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Added Jaylen Waddle trade")
    print("✅ Fixed DJ Moore trade team names")
    print("✅ All trades should now display correctly")

if __name__ == "__main__":
    fix_trades()