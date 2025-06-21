#!/usr/bin/env python3
"""
Static Site Generator for Fantasy Football League Website
Combines modular components into a single index.html file
"""

import os
import json
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class SiteGenerator:
    def __init__(self, base_path: str = None):
        """Initialize the site generator with paths"""
        self.base_path = Path(base_path) if base_path else Path(__file__).parent.parent
        self.src_path = self.base_path / 'src'
        self.dist_path = self.base_path / 'dist'
        self.components_path = self.src_path / 'components'
        self.data_path = self.src_path / 'data'
        self.js_path = self.src_path / 'js'
        self.styles_path = self.src_path / 'styles'
        
        # Ensure dist directory exists
        self.dist_path.mkdir(exist_ok=True)
        
        # Component cache
        self.components = {}
        self.data = {}
        
    def load_component(self, component_path: str) -> str:
        """Load a component file and cache it"""
        if component_path in self.components:
            return self.components[component_path]
            
        full_path = self.components_path / component_path
        if not full_path.exists():
            print(f"Warning: Component {component_path} not found")
            return f"<!-- Component {component_path} not found -->"
            
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        self.components[component_path] = content
        return content
        
    def load_data(self, data_file: str) -> Any:
        """Load JSON data file"""
        if data_file in self.data:
            return self.data[data_file]
            
        full_path = self.data_path / data_file
        if not full_path.exists():
            print(f"Warning: Data file {data_file} not found")
            return {}
            
        with open(full_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        self.data[data_file] = data
        return data
        
    def replace_placeholders(self, content: str, replacements: Dict[str, str]) -> str:
        """Replace placeholders in content"""
        for placeholder, value in replacements.items():
            content = content.replace(f"{{{{{placeholder}}}}}", str(value))
        return content
        
    def combine_css(self) -> str:
        """Combine all CSS files in order"""
        css_files = [
            'main.css',
            'components/trade-components.css',
            'components/draft-board.css',
            'components/player-journey.css',
            'components/network.css',
            'components/matchups.css',
            'components/modals.css'
        ]
        
        combined_css = []
        for css_file in css_files:
            css_path = self.styles_path / 'css' / css_file
            if css_path.exists():
                with open(css_path, 'r', encoding='utf-8') as f:
                    combined_css.append(f"/* {css_file} */\n{f.read()}")
            else:
                print(f"Warning: CSS file {css_file} not found")
                
        return '\n\n'.join(combined_css)
        
    def combine_js(self) -> str:
        """Combine JavaScript modules into single script"""
        js_modules = []
        
        # Load modules in dependency order
        module_order = [
            'modules/utils.js',
            'modules/firebase.js',
            'modules/modal.js',
            'modules/panels.js',
            'modules/charts.js',
            'modules/network.js',
            'modules/tradeHistory.js',
            'modules/matchups.js',
            'modules/draft.js',
            'modules/playerJourney.js',
            'modules/externalData.js',
            'main.js'
        ]
        
        for js_file in module_order:
            js_path = self.js_path / js_file
            if js_path.exists():
                with open(js_path, 'r', encoding='utf-8') as f:
                    # Remove export/import statements for combined file
                    content = f.read()
                    content = re.sub(r'^export\s+', '', content, flags=re.MULTILINE)
                    content = re.sub(r'^import\s+.*?;?\s*$', '', content, flags=re.MULTILINE)
                    js_modules.append(f"// {js_file}\n{content}")
            else:
                print(f"Warning: JS file {js_file} not found")
                
        return '\n\n'.join(js_modules)
        
    def generate_trade_items(self, trades_data: List[Dict]) -> str:
        """Generate HTML for all trade items"""
        trade_template = self.load_component('trades/trade-item.html')
        trade_items = []
        
        for i, trade in enumerate(trades_data):
            # Replace placeholders in trade template
            trade_html = self.replace_placeholders(trade_template, {
                'TRADE_ID': f'trade-{i}',
                'TRADE_DATE': trade.get('date', ''),
                'TEAM1_NAME': trade.get('team1', {}).get('name', ''),
                'TEAM2_NAME': trade.get('team2', {}).get('name', ''),
                'TEAM1_ASSETS': self.format_assets(trade.get('team1', {}).get('assets', [])),
                'TEAM2_ASSETS': self.format_assets(trade.get('team2', {}).get('assets', [])),
                'TRADE_GRADE_SLIDER': self.load_component('trades/trade-grade.html')
            })
            trade_items.append(trade_html)
            
        return '\n'.join(trade_items)
        
    def format_assets(self, assets: List[Dict]) -> str:
        """Format trade assets as HTML"""
        asset_html = []
        for asset in assets:
            if asset.get('type') == 'player':
                asset_html.append(f'<div class="player-asset">{asset.get("name", "Unknown Player")}</div>')
            elif asset.get('type') == 'draft_pick':
                pick_text = f"{asset.get('year', '')} Round {asset.get('round', '')} pick"
                if asset.get('original_owner'):
                    pick_text = f"{asset.get('original_owner')}'s {pick_text}"
                asset_html.append(f'<div class="pick-asset">{pick_text}</div>')
                
        return '\n'.join(asset_html)
        
    def build_site(self):
        """Build the complete site"""
        print("Starting site generation...")
        
        # Load base template
        base_html = self.load_component('base.html')
        
        # Load all panel components
        panels = {
            'OVERVIEW_PANEL': self.load_component('panels/overview.html'),
            'NETWORK_PANEL': self.load_component('panels/network.html'),
            'MATRIX_PANEL': self.load_component('panels/matrix.html'),
            'TIMELINE_PANEL': self.load_component('panels/timeline.html'),
            'PLAYERS_PANEL': self.load_component('panels/players.html'),
            'MATCHUPS_PANEL': self.load_component('panels/matchups.html'),
            'DRAFT_PANEL': self.load_component('panels/draft.html')
        }
        
        # Load shared components
        shared = {
            'HEADER': self.load_component('header.html'),
            'CONTROLS': self.load_component('shared/controls.html'),
            'MODALS': self.load_component('shared/modals.html')
        }
        
        # Load trade data (placeholder - integrate with your existing data)
        # trades_data = self.load_data('trades.json')
        
        # Combine all CSS
        combined_css = self.combine_css()
        
        # Combine all JavaScript
        combined_js = self.combine_js()
        
        # Create replacements dictionary
        replacements = {
            'SITE_TITLE': 'Eazy Pickens',
            'COMBINED_CSS': f'<style>\n{combined_css}\n</style>',
            'COMBINED_JS': f'<script>\n{combined_js}\n</script>',
            'BUILD_TIME': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            **panels,
            **shared,
            # Add data placeholders
            'TOTAL_TRADES': '159',  # Replace with actual data
            'TOTAL_PLAYERS': '234',  # Replace with actual data
            'TOTAL_PICKS': '87',    # Replace with actual data
            'TRADE_HISTORY': '<!-- Trade items will be generated here -->'
        }
        
        # Replace all placeholders
        final_html = self.replace_placeholders(base_html, replacements)
        
        # Write to dist
        output_path = self.dist_path / 'index.html'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_html)
            
        print(f"Site generated successfully: {output_path}")
        print(f"File size: {output_path.stat().st_size / 1024:.1f} KB")
        
    def update_section(self, section: str, content: str):
        """Update a specific section without regenerating entire site"""
        # Read current index.html
        index_path = self.dist_path / 'index.html'
        if not index_path.exists():
            print("No index.html found. Running full build...")
            self.build_site()
            return
            
        with open(index_path, 'r', encoding='utf-8') as f:
            current_html = f.read()
            
        # Define section markers
        markers = {
            'trades': ('<!-- TRADE_HISTORY_START -->', '<!-- TRADE_HISTORY_END -->'),
            'network': ('<!-- NETWORK_DATA_START -->', '<!-- NETWORK_DATA_END -->'),
            'matchups': ('<!-- MATCHUPS_DATA_START -->', '<!-- MATCHUPS_DATA_END -->'),
            'draft': ('<!-- DRAFT_DATA_START -->', '<!-- DRAFT_DATA_END -->')
        }
        
        if section not in markers:
            print(f"Unknown section: {section}")
            return
            
        start_marker, end_marker = markers[section]
        
        # Find and replace section
        start_idx = current_html.find(start_marker)
        end_idx = current_html.find(end_marker)
        
        if start_idx == -1 or end_idx == -1:
            print(f"Section markers not found for {section}")
            return
            
        # Replace section content
        new_html = (
            current_html[:start_idx + len(start_marker)] +
            '\n' + content + '\n' +
            current_html[end_idx:]
        )
        
        # Write updated HTML
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(new_html)
            
        print(f"Updated section: {section}")
        

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Static Site Generator')
    parser.add_argument('--build', action='store_true', help='Build complete site')
    parser.add_argument('--update', type=str, help='Update specific section')
    parser.add_argument('--content', type=str, help='Content for update (file path or string)')
    parser.add_argument('--watch', action='store_true', help='Watch for changes and rebuild')
    
    args = parser.parse_args()
    
    generator = SiteGenerator()
    
    if args.build:
        generator.build_site()
    elif args.update and args.content:
        if os.path.exists(args.content):
            with open(args.content, 'r') as f:
                content = f.read()
        else:
            content = args.content
        generator.update_section(args.update, content)
    elif args.watch:
        print("Watch mode not implemented yet")
    else:
        # Default to build
        generator.build_site()
        

if __name__ == '__main__':
    main()