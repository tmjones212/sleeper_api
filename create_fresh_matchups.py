#!/usr/bin/env python3
"""Create a fresh, minimal matchups panel HTML snippet"""

matchups_html = '''
<!-- Matchups Panel -->
<div class="visualization-panel" id="matchups-panel">
    <div class="panel-header">
        <h2>⚔️ League Matchups</h2>
        <p>View matchup history across all years</p>
    </div>
    <div class="panel-content">
        <div class="search-container">
            <label for="matchupYearSelect">Select Year:</label>
            <select id="matchupYearSelect" onchange="window.showMatchupYear()">
                <option value="all">All Years</option>
                <option value="2024" selected>2024</option>
                <option value="2023">2023</option>
                <option value="2022">2022</option>
            </select>
        </div>
        
        <div id="matchupsContainer" style="margin-top: 20px;">
            <div class="year-matchups" data-year="2024" style="display: block;">
                <h3>📅 2024 Season</h3>
                <div class="week-card" style="background: #2d2d2d; padding: 15px; margin: 10px 0; border-radius: 10px;">
                    <h4 style="color: #0066cc;">Week 1</h4>
                    <div class="matchup-card" style="background: #404040; padding: 10px; margin: 5px 0; border-radius: 5px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="flex: 1; text-align: center;">
                                <div style="font-weight: bold;">Team A</div>
                                <div style="font-size: 1.2rem;">100.0</div>
                            </div>
                            <div style="padding: 0 10px;">vs</div>
                            <div style="flex: 1; text-align: center;">
                                <div style="font-weight: bold;">Team B</div>
                                <div style="font-size: 1.2rem;">95.0</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Draft Panel -->
<div class="visualization-panel" id="draft-panel">
    <div class="panel-header">
        <h2>🏈 Draft Results</h2>
        <p>View draft picks by year</p>
    </div>
    <div class="panel-content">
        <div class="search-container">
            <label for="draftYearSelect">Select Year:</label>
            <select id="draftYearSelect" onchange="window.showDraftYear()">
                <option value="2025">2025</option>
                <option value="2024" selected>2024</option>
                <option value="2023">2023</option>
                <option value="2022">2022</option>
            </select>
        </div>
        <div id="draftResults" style="margin-top: 20px;">
            <div style="text-align: center; padding: 40px;">
                <h3>Loading draft data...</h3>
            </div>
        </div>
    </div>
</div>
'''

print("Fresh panel HTML created. This can be used to replace the existing panels if needed.")
print("\nKey differences in this fresh version:")
print("1. Simplified structure with no nested complexity")
print("2. Inline styles to ensure visibility")
print("3. Minimal test data to verify rendering")
print("4. Clear div hierarchy")

# Save to file
with open('fresh_panels.html', 'w') as f:
    f.write(matchups_html)
    print("\nSaved to fresh_panels.html")