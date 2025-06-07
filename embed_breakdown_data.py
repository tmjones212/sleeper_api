#!/usr/bin/env python3
"""
Create a JavaScript variable with matchup breakdown data to embed directly in HTML
"""

import json
import os

def create_embedded_breakdown_data():
    """Create a compressed JavaScript version of the breakdown data"""
    
    # Load the breakdown data
    breakdowns_file = "/home/alaba/coolProjects/matchup_breakdowns.json"
    with open(breakdowns_file, 'r') as f:
        data = json.load(f)
    
    all_matchups = data.get('matchups', {})
    
    # Filter to only include current league and recent data
    current_league = "1181025001438806016"
    old_league = "1048308938824937472"  # Keep some old data for demo
    
    matchups = {}
    for key, value in all_matchups.items():
        # Include current league data and some old league data (first 10 weeks for demo)
        if current_league in key or (old_league in key and "_" in key):
            week_num = int(key.split("_")[1]) if "_" in key else 1
            if current_league in key or week_num <= 10:
                matchups[key] = value
    
    # Create JavaScript variable declaration
    js_content = "const MATCHUP_BREAKDOWNS = " + json.dumps(matchups, separators=(',', ':')) + ";\n"
    
    # Write to a JavaScript file
    output_file = "/home/alaba/coolProjects/matchup_breakdowns.js"
    with open(output_file, 'w') as f:
        f.write(js_content)
    
    print(f"✅ Created embedded breakdown data: {output_file}")
    print(f"📊 Data size: {len(js_content):,} characters")
    print(f"📁 Weeks included: {len(matchups)}")
    
    # Show sample key
    if matchups:
        sample_key = list(matchups.keys())[0]
        sample_data = matchups[sample_key][0] if matchups[sample_key] else {}
        print(f"🔍 Sample key: {sample_key}")
        print(f"🏈 Sample team: Roster {sample_data.get('roster_id', 'N/A')} - {sample_data.get('total_points', 'N/A')} pts")

if __name__ == "__main__":
    create_embedded_breakdown_data()