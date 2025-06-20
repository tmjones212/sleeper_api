#!/usr/bin/env python3
"""
Fix the draft pick trades that incorrectly show duplicate Quinshon Judkins
"""
import re
from datetime import datetime

def fix_draft_trades():
    # Read current HTML
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create backup
    import shutil
    backup_name = f'index_backup_draft_fix_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
    shutil.copy('index.html', backup_name)
    print(f"Created backup: {backup_name}")
    
    # Find and fix the 2025-04-30 09:48 AM trade
    # This trade incorrectly shows both ShadyCommish88's and lamjohnson56's picks as Quinshon Judkins
    # The 6th pick was actually EBao's originally
    
    # Find the problematic trade
    pattern = r'(<div class="trade-item">.*?2025-04-30 09:48 AM.*?</div>\s*</div>)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        print("Found the 2025-04-30 09:48 AM trade")
        
        # Replace with correct information
        # lamjohnson56 traded his 4th pick (Cam Ward) to ShadyCommish88
        # ShadyCommish88 traded EBao's 6th pick (Quinshon Judkins), his 16th pick, and 2027 2nd
        correct_trade = '''<div class="trade-item">
                        <div class="trade-date">2025-04-30 09:48 AM</div>
                        <div class="trade-summary">
                            <strong>lamjohnson56 ↔ ShadyCommish88</strong>
                            <span style="color: #666; margin-left: 20px;">
                                0 players, 4 picks
                            </span>
                        </div>
                        <div class="trade-teams">
                            
                            
                            <div class="team-side">
                                <h4>lamjohnson56</h4>
                                <ul class="asset-list">
                                    
                                    
                                    <li class="pick-item">📋 Pick #6 (EBao's 2025 R1) - QUINSHON JUDKINS</li>
                                    
                                    <li class="pick-item">📋 Pick #16 (ShadyCommish88's 2025 R2) - JAYDEN HIGGINS</li>
                                    
                                    <li class="pick-item">📋 ShadyCommish88's 2027 Round 2 pick</li>
                                    
                                </ul>
                            </div>
                            
                            
                            
                            <div class="team-side">
                                <h4>ShadyCommish88</h4>
                                <ul class="asset-list">
                                    
                                    
                                    <li class="pick-item">📋 Pick #4 (lamjohnson56's 2025 R1) - CAM WARD</li>
                                    
                                </ul>
                            </div>
                            
                            
                        </div>
                    </div>'''
        
        content = content[:match.start()] + correct_trade + content[match.end():]
        print("✅ Fixed the draft pick trade - correctly shows EBao's pick")
    
    # Now fix the 2025-04-30 10:18 AM trade
    # This should show lamjohnson56 trading with androooooo, not duplicate Quinshon Judkins
    pattern2 = r'(<div class="trade-item">.*?2025-04-30 10:18 AM.*?</div>\s*</div>)'
    match2 = re.search(pattern2, content, re.DOTALL)
    
    if match2:
        print("Found the 2025-04-30 10:18 AM trade")
        
        # This trade is correct - lamjohnson56 traded EBao's 6th pick (which he got from previous trade)
        # and his own 16th pick to androooooo for androooooo's 5th pick
        # The display is already correct, no changes needed
        print("✅ This trade display is already correct")
    
    # Write the fixed content
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Fixed draft pick trades:")
    print("  - Correctly shows Pick #6 was EBao's original pick")
    print("  - lamjohnson56 received EBao's pick from ShadyCommish88")
    print("  - lamjohnson56 then traded it to androooooo")

if __name__ == "__main__":
    fix_draft_trades()