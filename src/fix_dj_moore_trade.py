#!/usr/bin/env python3
"""
Fix the DJ Moore trade to show correct assets on each side.
"""
import re

def fix_dj_moore_trade(html_content):
    """Fix the specific DJ Moore trade display."""
    
    # Find the DJ Moore trade section
    # Look for the pattern where ShadyCommish88 incorrectly receives both DJ Moore and a pick
    pattern = r'(<div class="team-side">\s*<h4>ShadyCommish88</h4>.*?Receives:.*?DJ MOORE.*?</span>\s*</li>\s*)(<li class="pick-item">📋 EBao\'s 2026 Round 2 pick</li>)'
    
    # First, remove the pick from ShadyCommish88's receives (they should only get picks, not DJ Moore)
    # Actually, based on user's description, we need to swap it:
    # emanueljd3 should get DJ Moore
    # ShadyCommish88 should get both 2026 2nd round picks
    
    # Let's find and fix the whole trade section
    # Pattern to match the entire trade block
    trade_pattern = r'(2025-06-12.*?ShadyCommish88 ↔ emanueljd3.*?)(</div>\s*<div class="trade-grade-container">)'
    
    def replace_trade(match):
        trade_start = match.group(1)
        trade_end = match.group(2)
        
        # Build the corrected trade HTML
        corrected_trade = '''<div class="team-side">
                                <h4>ShadyCommish88</h4>
                                <div style="color: #66ff66; margin: 5px 0;">Receives:</div>
                                <ul class="asset-list">
                                    <li class="pick-item">📋 EBao's 2026 Round 2 pick</li>
                                    <li class="pick-item">📋 ShadyCommish88's 2026 Round 2 pick</li>
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
                        </div>'''
        
        # Extract the beginning of the trade
        trade_beginning = re.search(r'(.*?<div class="trade-teams">)', trade_start, re.DOTALL)
        if trade_beginning:
            return trade_beginning.group(1) + corrected_trade + trade_end
        
        return match.group(0)  # Return original if pattern doesn't match
    
    # Apply the fix
    updated_html = re.sub(trade_pattern, replace_trade, html_content, flags=re.DOTALL)
    
    return updated_html

def main():
    print("Fixing DJ Moore trade...")
    
    # Read existing index.html
    with open('../index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Fix the trade
    updated_html = fix_dj_moore_trade(html_content)
    
    # Write back to index.html
    with open('../index.html', 'w', encoding='utf-8') as f:
        f.write(updated_html)
    
    print("Successfully fixed DJ Moore trade!")

if __name__ == "__main__":
    main()