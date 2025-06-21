#!/usr/bin/env python3
"""
Matchups-specific update script
Updates matchup data without touching other sections
"""

import sys
import os
from pathlib import Path
import json

# Add paths
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))
sys.path.append(str(Path(__file__).parent.parent / 'build'))

from component_updater import ComponentUpdater
from matchup_service import MatchupService
from client import SleeperAPI

class MatchupUpdater:
    def __init__(self, league_id: str):
        self.league_id = league_id
        self.updater = ComponentUpdater()
        self.api = SleeperAPI(league_id)
        self.service = MatchupService(self.api, league_id)
        
    def update_matchups(self):
        """Update matchup data and regenerate matchup panel"""
        print(f"Updating matchups for league {self.league_id}...")
        
        # Get all matchup data
        all_matchups = self.service.get_all_matchups()
        
        # Generate matchup breakdowns file
        breakdowns_path = Path(__file__).parent.parent / 'dist' / 'matchup_breakdowns.js'
        
        # Format data for JavaScript
        js_content = f"// Generated matchup data for league {self.league_id}\n"
        js_content += "const matchupData = " + json.dumps(all_matchups, indent=2) + ";\n"
        
        with open(breakdowns_path, 'w') as f:
            f.write(js_content)
            
        print(f"✓ Updated matchup_breakdowns.js with {len(all_matchups)} seasons of data")
        
        # Update the matchups panel in index.html
        self.updater.update_component('matchups')
        

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Update matchup data')
    parser.add_argument('--league', '-l', required=True, help='Sleeper league ID')
    
    args = parser.parse_args()
    
    updater = MatchupUpdater(args.league)
    updater.update_matchups()
    

if __name__ == '__main__':
    main()