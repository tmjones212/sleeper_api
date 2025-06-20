#!/usr/bin/env python3
"""
Add June 2025 trades to index.html while preserving all existing content and trade sliders
"""
import re

def add_june_2025_trades():
    # Read the current index.html
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # June 2025 trades HTML with proper trade sliders
    june_trades_html = '''
                    <!-- June 2025 Trades -->
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

                    <div class="trade-item">
                        <div class="trade-date">2025-06-13 01:13 AM</div>
                        <div class="trade-summary">
                            <strong>BaoDown ↔ lamjohnson56</strong>
                            <span style="color: #666; margin-left: 20px;">
                                2 players, 0 picks
                            </span>
                        </div>
                        <div class="trade-teams">
                            <div class="team-side">
                                <h4>BaoDown</h4>
                                <div style="color: #66ff66; margin: 5px 0;">Receives:</div>
                                <ul class="asset-list">
                                    <li class="player-item" style="display: flex; align-items: center; gap: 8px; padding: 5px 0;">
                                        <img src="https://sleepercdn.com/content/nfl/players/thumb/7527.jpg" 
                                             style="width: 24px; height: 24px; border-radius: 50%; object-fit: cover;" 
                                             onerror="this.outerHTML='<span style=&quot;color: #66ff66;&quot;>🏈</span>'"
                                             alt="MAC JONES">
                                        <span>MAC JONES</span>
                                    </li>
                                </ul>
                            </div>
                            
                            <div class="team-side">
                                <h4>lamjohnson56</h4>
                                <div style="color: #66ff66; margin: 5px 0;">Receives:</div>
                                <ul class="asset-list">
                                    <li class="player-item" style="display: flex; align-items: center; gap: 8px; padding: 5px 0;">
                                        <img src="https://sleepercdn.com/content/nfl/players/thumb/9999.jpg" 
                                             style="width: 24px; height: 24px; border-radius: 50%; object-fit: cover;" 
                                             onerror="this.outerHTML='<span style=&quot;color: #66ff66;&quot;>🏈</span>'"
                                             alt="WILL LEVIS">
                                        <span>WILL LEVIS</span>
                                    </li>
                                </ul>
                            </div>
                        </div>
                        <div class="trade-grade-container">
                            <div style="margin-bottom: 8px; color: #e0e0e0; font-weight: 600;">👤 Your Trade Grade:</div>
                            <input type="range" min="0" max="100" value="50" class="trade-grade-slider" 
                                   id="trade-grade-levis" onchange="updateTradeGrade('levis', this.value)">
                            <div class="trade-grade-labels">
                                <span>BaoDown Won</span>
                                <span>Even</span>
                                <span>lamjohnson56 Won</span>
                            </div>
                            <div class="trade-grade-result" id="trade-result-levis">
                                <span style="color: #999999;">Move slider to grade</span>
                            </div>
                        </div>
                    </div>

                    <div class="trade-item">
                        <div class="trade-date">2025-06-12 08:21 PM</div>
                        <div class="trade-summary">
                            <strong>tmjones212 ↔ emanueljd3</strong>
                            <span style="color: #666; margin-left: 20px;">
                                1 players, 2 picks
                            </span>
                        </div>
                        <div class="trade-teams">
                            <div class="team-side">
                                <h4>tmjones212</h4>
                                <div style="color: #66ff66; margin: 5px 0;">Receives:</div>
                                <ul class="asset-list">
                                    <li class="pick-item">📋 EBao's 2026 Round 2 pick</li>
                                    <li class="pick-item">📋 tmjones212's 2026 Round 2 pick</li>
                                </ul>
                            </div>
                            
                            <div class="team-side">
                                <h4>emanueljd3</h4>
                                <div style="color: #66ff66; margin: 5px 0;">Receives:</div>
                                <ul class="asset-list">
                                    <li class="player-item" style="display: flex; align-items: center; gap: 8px; padding: 5px 0;">
                                        <img src="https://sleepercdn.com/content/nfl/players/thumb/4983.jpg" 
                                             style="width: 24px; height: 24px; border-radius: 50%; object-fit: cover;" 
                                             onerror="this.outerHTML='<span style=&quot;color: #66ff66;&quot;>🏈</span>'"
                                             alt="DJ MOORE">
                                        <span>DJ MOORE</span>
                                    </li>
                                </ul>
                            </div>
                        </div>
                        <div class="trade-grade-container">
                            <div style="margin-bottom: 8px; color: #e0e0e0; font-weight: 600;">👤 Your Trade Grade:</div>
                            <input type="range" min="0" max="100" value="50" class="trade-grade-slider" 
                                   id="trade-grade-djmoore" onchange="updateTradeGrade('djmoore', this.value)">
                            <div class="trade-grade-labels">
                                <span>tmjones212 Won</span>
                                <span>Even</span>
                                <span>emanueljd3 Won</span>
                            </div>
                            <div class="trade-grade-result" id="trade-result-djmoore">
                                <span style="color: #999999;">Move slider to grade</span>
                            </div>
                        </div>
                    </div>

'''
    
    # Find the timeline container
    timeline_start = content.find('<div class="timeline-container">')
    if timeline_start == -1:
        print("ERROR: Could not find timeline container")
        return False
    
    # Find the first trade item
    first_trade = content.find('<div class="trade-item">', timeline_start)
    if first_trade == -1:
        print("ERROR: Could not find any trade items")
        return False
    
    # Check if June 2025 trades already exist
    if '2025-06-16 04:18 PM' in content:
        print("June 2025 trades already exist, skipping...")
        return True
    
    # Insert the June trades at the beginning of the timeline (after timeline-container opening)
    insert_pos = content.find('\n', timeline_start) + 1
    new_content = content[:insert_pos] + june_trades_html + content[insert_pos:]
    
    # Write the updated content
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Successfully added June 2025 trades:")
    print("  - Jaylen Waddle trade (Halteclere ↔ lamjohnson56)")
    print("  - Will Levis/Mac Jones trade (BaoDown ↔ lamjohnson56)")
    print("  - DJ Moore trade (tmjones212 ↔ emanueljd3) with BOTH picks")
    print("✅ All trade grade sliders preserved")
    
    return True

if __name__ == "__main__":
    add_june_2025_trades()