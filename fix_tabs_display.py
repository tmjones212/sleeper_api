#!/usr/bin/env python3
"""
Fix the matchups and draft tabs display issue in index.html
"""

import re
import shutil
from datetime import datetime

def fix_tabs_display():
    """Fix the display issue with matchups and draft tabs"""
    
    # Backup the current file
    backup_name = f"index_backup_tabs_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    shutil.copy('index.html', backup_name)
    print(f"Created backup: {backup_name}")
    
    # Read the current HTML
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Find and fix the duplicate showPanel functions
    # Count how many showPanel functions exist
    showpanel_matches = list(re.finditer(r'function showPanel\(panelName\)\s*{', html))
    print(f"Found {len(showpanel_matches)} showPanel function definitions")
    
    if len(showpanel_matches) > 1:
        # Keep only the first (most complete) one
        print("Removing duplicate showPanel functions...")
        # Start from the last match and work backwards
        for match in reversed(showpanel_matches[1:]):
            # Find the end of this function
            start = match.start()
            brace_count = 0
            i = match.end()
            while i < len(html):
                if html[i] == '{':
                    brace_count += 1
                elif html[i] == '}':
                    if brace_count == 0:
                        # Found the closing brace
                        end = i + 1
                        # Remove this duplicate function
                        html = html[:start] + html[end:]
                        break
                    else:
                        brace_count -= 1
                i += 1
    
    # Add a fix to ensure panels initialize properly
    init_fix = """
        // Fix for matchups and draft tabs
        function ensureTabsWork() {
            console.log('Ensuring tabs work properly...');
            
            // Re-initialize when switching to matchups or draft
            const _showPanel = window.showPanel;
            window.showPanel = function(panelName) {
                console.log('Switching to panel:', panelName);
                
                // Call original function
                _showPanel(panelName);
                
                // Special handling for matchups and draft
                setTimeout(() => {
                    if (panelName === 'matchups' && typeof showMatchupYear === 'function') {
                        console.log('Initializing matchups tab...');
                        showMatchupYear();
                    }
                    if (panelName === 'draft' && typeof showDraftYear === 'function') {
                        console.log('Initializing draft tab...');
                        showDraftYear();
                    }
                }, 100);
            };
        }
        
        // Call on page load
        document.addEventListener('DOMContentLoaded', function() {
            ensureTabsWork();
        });
    """
    
    # Insert the fix before the closing script tag
    last_script_close = html.rfind('</script>')
    if last_script_close != -1:
        html = html[:last_script_close] + init_fix + html[last_script_close:]
        print("Added initialization fix")
    
    # Write the fixed HTML
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("Fixed index.html successfully!")
    print("\nWhat was fixed:")
    print("1. Removed duplicate showPanel functions")
    print("2. Added initialization code to ensure matchups and draft tabs work")
    print("3. Added re-initialization when switching to these tabs")

if __name__ == "__main__":
    fix_tabs_display()