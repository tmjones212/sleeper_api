#!/usr/bin/env python3
"""
Trade-specific update script
Updates only trade data while preserving Firebase code and trade rating sliders
"""

import sys
import os
from pathlib import Path

# Add paths
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))
sys.path.append(str(Path(__file__).parent.parent / 'build'))

from component_updater import ComponentUpdater
from transaction_service import TransactionService
from client import SleeperAPI
import json
import re

class TradeUpdater:
    def __init__(self, league_id: str):
        self.league_id = league_id
        self.updater = ComponentUpdater()
        self.api = SleeperAPI(league_id)
        self.service = TransactionService(self.api)
        
    def generate_trade_html(self, trades):
        """Generate HTML for trades using the template"""
        template_path = Path(__file__).parent.parent / 'src' / 'components' / 'trades' / 'trade-item.html'
        
        if not template_path.exists():
            print("Error: Trade template not found")
            return ""
            
        with open(template_path, 'r') as f:
            template = f.read()
            
        trade_html_items = []
        
        for i, trade in enumerate(trades):
            # Extract team data
            teams = list(trade.get('team_assets', {}).keys())
            if len(teams) < 2:
                continue
                
            team1_name = teams[0]
            team2_name = teams[1]
            
            # Get assets for each team
            team1_assets = trade['team_assets'][team1_name]
            team2_assets = trade['team_assets'][team2_name]
            
            # Format assets HTML
            team1_gives_html = self.format_assets(team1_assets.get('gives', []))
            team1_receives_html = self.format_assets(team1_assets.get('receives', []))
            team2_gives_html = self.format_assets(team2_assets.get('gives', []))
            team2_receives_html = self.format_assets(team2_assets.get('receives', []))
            
            # Format date
            date_str = trade.get('date', 'Unknown Date')
            
            # Create trade HTML from template
            trade_html = template
            trade_html = trade_html.replace('{{TRADE_ID}}', f'trade-{i}')
            trade_html = trade_html.replace('{{TRADE_DATE}}', date_str)
            trade_html = trade_html.replace('{{TEAM1_NAME}}', team1_name)
            trade_html = trade_html.replace('{{TEAM2_NAME}}', team2_name)
            trade_html = trade_html.replace('{{TEAM1_GIVES}}', team1_gives_html)
            trade_html = trade_html.replace('{{TEAM1_RECEIVES}}', team1_receives_html)
            trade_html = trade_html.replace('{{TEAM2_GIVES}}', team2_gives_html)
            trade_html = trade_html.replace('{{TEAM2_RECEIVES}}', team2_receives_html)
            
            # Add trade grading slider
            grade_html = f'''
            <div class="trade-grade">
                <label>Rate this trade:</label>
                <input type="range" id="grade-{i}" class="grade-slider" 
                       min="0" max="10" value="5" step="0.5"
                       onchange="saveTradeGradeToFirebase('{self.league_id}', {i}, this.value)">
                <span class="grade-value">5.0</span>
            </div>
            '''
            trade_html = trade_html.replace('{{TRADE_GRADE_SLIDER}}', grade_html)
            
            trade_html_items.append(trade_html)
            
        return '\n'.join(trade_html_items)
        
    def format_assets(self, assets):
        """Format assets as HTML"""
        if not assets:
            return '<div class="no-assets">Nothing</div>'
            
        asset_items = []
        for asset in assets:
            if asset.get('type') == 'player':
                name = asset.get('player_name', 'Unknown Player')
                asset_items.append(f'<div class="asset-item player">{name}</div>')
            elif asset.get('type') == 'draft_pick':
                season = asset.get('season', 'Unknown')
                round_num = asset.get('round', 'Unknown')
                original_owner = asset.get('original_owner', '')
                
                if original_owner:
                    pick_text = f"{original_owner}'s {season} Round {round_num} pick"
                else:
                    pick_text = f"{season} Round {round_num} pick"
                    
                asset_items.append(f'<div class="asset-item draft-pick">{pick_text}</div>')
                
        return '\n'.join(asset_items)
        
    def update_trades(self, preserve_grades=True):
        """Update trades in the website"""
        print(f"Fetching trades for league {self.league_id}...")
        
        # Get fresh trade data
        trades = self.service.get_trades(self.league_id)
        print(f"Found {len(trades)} trades")
        
        # Read current index.html to preserve grades
        index_path = Path(__file__).parent.parent / 'dist' / 'index.html'
        existing_grades = {}
        
        if index_path.exists() and preserve_grades:
            with open(index_path, 'r') as f:
                content = f.read()
                
            # Extract existing grades
            grade_pattern = r'<input[^>]*id="grade-(\d+)"[^>]*value="([^"]*)"'
            for match in re.finditer(grade_pattern, content):
                trade_id = int(match.group(1))
                grade_value = match.group(2)
                existing_grades[trade_id] = grade_value
                
            print(f"Preserved {len(existing_grades)} existing trade grades")
        
        # Generate new trade HTML
        trade_html = self.generate_trade_html(trades)
        
        # Restore grades in the new HTML
        if existing_grades:
            for trade_id, grade_value in existing_grades.items():
                # Update the value in the slider
                pattern = rf'(id="grade-{trade_id}"[^>]*value=")[^"]*(")'
                trade_html = re.sub(pattern, rf'\g<1>{grade_value}\g<2>', trade_html)
                
                # Update the displayed value
                pattern2 = rf'(id="grade-{trade_id}"[^>]*>[\s\S]*?<span class="grade-value">)[^<]*(</span>)'
                trade_html = re.sub(pattern2, rf'\g<1>{grade_value}\g<2>', trade_html)
        
        # Update the trade section in index.html
        if index_path.exists():
            with open(index_path, 'r') as f:
                full_content = f.read()
                
            # Find and replace trade history section
            start_marker = '<!-- TRADE_HISTORY_START -->'
            end_marker = '<!-- TRADE_HISTORY_END -->'
            
            start_idx = full_content.find(start_marker)
            end_idx = full_content.find(end_marker)
            
            if start_idx != -1 and end_idx != -1:
                new_content = (
                    full_content[:start_idx + len(start_marker)] +
                    '\n' + trade_html + '\n' +
                    full_content[end_idx:]
                )
                
                with open(index_path, 'w') as f:
                    f.write(new_content)
                    
                print("✓ Trade section updated successfully")
                if existing_grades:
                    print(f"✓ Restored {len(existing_grades)} trade grades")
            else:
                print("Error: Trade history markers not found in index.html")
                print("Adding markers and trade content...")
                
                # Find trade-history div
                trade_div_pattern = r'<div[^>]*id="trade-history"[^>]*>'
                match = re.search(trade_div_pattern, full_content)
                
                if match:
                    insert_pos = match.end()
                    marked_trades = f'\n{start_marker}\n{trade_html}\n{end_marker}\n'
                    new_content = full_content[:insert_pos] + marked_trades + full_content[insert_pos:]
                    
                    with open(index_path, 'w') as f:
                        f.write(new_content)
                        
                    print("✓ Added trade history with markers")
        else:
            print("Error: index.html not found. Run site_generator.py first.")
            

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Update trade data only')
    parser.add_argument('--league', '-l', required=True, help='Sleeper league ID')
    parser.add_argument('--no-preserve-grades', action='store_true', 
                       help='Do not preserve existing trade grades')
    
    args = parser.parse_args()
    
    updater = TradeUpdater(args.league)
    updater.update_trades(preserve_grades=not args.no_preserve_grades)
    

if __name__ == '__main__':
    main()