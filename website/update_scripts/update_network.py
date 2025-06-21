#!/usr/bin/env python3
"""
Network visualization update script
Updates network data without regenerating entire site
"""

import sys
import os
from pathlib import Path
import json
import re

# Add paths
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))
sys.path.append(str(Path(__file__).parent.parent / 'build'))

from component_updater import ComponentUpdater
from trade_visualization_service import LeagueVisualizationService
from client import SleeperAPI

class NetworkUpdater:
    def __init__(self, league_id: str):
        self.league_id = league_id
        self.updater = ComponentUpdater()
        self.api = SleeperAPI(league_id)
        self.service = LeagueVisualizationService(self.api)
        
    def update_network(self):
        """Update network visualization data"""
        print(f"Updating network data for league {self.league_id}...")
        
        # Get network data
        network_data = self.service.get_trade_network_data(self.league_id)
        
        # Read current index.html
        index_path = Path(__file__).parent.parent / 'dist' / 'index.html'
        
        if not index_path.exists():
            print("Error: index.html not found. Run site_generator.py first.")
            return
            
        with open(index_path, 'r') as f:
            content = f.read()
            
        # Find and update networkData variable
        # Look for pattern: const networkData = {...}
        pattern = r'(const networkData = )({[\s\S]*?})(;[\s\S]*?// End network data)'
        
        # Format new network data
        new_data_str = json.dumps(network_data, indent=4)
        replacement = rf'\g<1>{new_data_str}\g<3>'
        
        # Replace the data
        new_content = re.sub(pattern, replacement, content)
        
        # If pattern not found, try to add it
        if new_content == content:
            print("Network data pattern not found, adding it...")
            
            # Find where to insert (after the firebase script but before other scripts)
            insert_marker = '<!-- NETWORK_DATA_START -->'
            if insert_marker in content:
                insert_pos = content.find(insert_marker) + len(insert_marker)
                network_script = f'\n<script>\nconst networkData = {new_data_str};\n// End network data\n</script>\n'
                new_content = content[:insert_pos] + network_script + content[insert_pos:]
            else:
                print("Error: Could not find insertion point for network data")
                return
                
        # Write updated content
        with open(index_path, 'w') as f:
            f.write(new_content)
            
        print(f"✓ Updated network data:")
        print(f"  - {len(network_data.get('nodes', []))} nodes (teams)")
        print(f"  - {len(network_data.get('links', []))} links (trades)")
        

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Update network visualization data')
    parser.add_argument('--league', '-l', required=True, help='Sleeper league ID')
    
    args = parser.parse_args()
    
    updater = NetworkUpdater(args.league)
    updater.update_network()
    

if __name__ == '__main__':
    main()