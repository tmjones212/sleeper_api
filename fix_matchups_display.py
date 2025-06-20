#!/usr/bin/env python3
"""Fix the matchups and draft tab display issue"""

with open('index.html', 'r') as f:
    content = f.read()

# Find the showMatchupYear function and make it force display
old_pattern = '''        window.showMatchupYear = function showMatchupYear() {
            const yearSelect = document.getElementById('matchupYearSelect');
            if (!yearSelect) {
                console.log('Year selector not found');
                return;
            }
            
            const selectedYear = yearSelect.value;
            const yearMatchups = document.querySelectorAll('.year-matchups');'''

new_pattern = '''        window.showMatchupYear = function showMatchupYear() {
            const yearSelect = document.getElementById('matchupYearSelect');
            if (!yearSelect) {
                console.log('Year selector not found');
                return;
            }
            
            const selectedYear = yearSelect.value;
            const yearMatchups = document.querySelectorAll('.year-matchups');
            
            // Force display to ensure visibility
            const container = document.getElementById('matchupsContainer');
            if (container) {
                container.style.display = 'block';
            }'''

content = content.replace(old_pattern, new_pattern)

# Also ensure the panel display is forced
old_panel = '''            } else if (panelName === 'matchups') {
                // Initialize matchups if needed
                console.log('🎯 Matchups panel activated');
                // Call immediately and also with a small delay as backup
                if (typeof window.showMatchupYear === 'function') {
                    console.log('Calling showMatchupYear immediately...');
                    window.showMatchupYear();
                } else {
                    console.error('ERROR: showMatchupYear function not found!');
                    console.log('Available functions:', Object.keys(window).filter(k => k.includes('show')));
                }
                // Also call with delay as backup
                setTimeout(() => {
                    if (typeof window.showMatchupYear === 'function') {
                        window.showMatchupYear();
                    }
                }, 100);'''

new_panel = '''            } else if (panelName === 'matchups') {
                // Initialize matchups if needed
                console.log('🎯 Matchups panel activated');
                // Force immediate display
                const matchupsContainer = document.getElementById('matchupsContainer');
                if (matchupsContainer) {
                    matchupsContainer.style.display = 'block';
                }
                // Call the function immediately
                if (window.showMatchupYear) {
                    window.showMatchupYear();
                } else {
                    // Fallback: manually show 2024 data
                    const yearMatchups = document.querySelectorAll('.year-matchups[data-year="2024"]');
                    yearMatchups.forEach(div => {
                        div.style.display = 'block';
                    });
                }'''

content = content.replace(old_panel, new_panel)

# Write the fixed content
with open('index.html', 'w') as f:
    f.write(content)

print("Fixed matchups display issue")