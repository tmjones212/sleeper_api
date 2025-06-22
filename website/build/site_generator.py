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
from html.parser import HTMLParser

class TradeExtractor(HTMLParser):
    """Extract trade items from HTML"""
    def __init__(self):
        super().__init__()
        self.in_trade_item = False
        self.in_timeline = False
        self.trade_items = []
        self.current_trade = []
        self.depth = 0
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        if tag == 'div' and attrs_dict.get('class') == 'timeline-container':
            self.in_timeline = True
            
        if self.in_timeline and tag == 'div' and attrs_dict.get('class') == 'trade-item':
            self.in_trade_item = True
            self.depth = 0
            self.current_trade = ['<div class="trade-item">']
            
        elif self.in_trade_item:
            self.depth += 1 if tag == 'div' else 0
            attr_str = ' '.join([f'{k}="{v}"' for k, v in attrs])
            if attr_str:
                self.current_trade.append(f'<{tag} {attr_str}>')
            else:
                self.current_trade.append(f'<{tag}>')
                
    def handle_endtag(self, tag):
        if self.in_trade_item:
            self.current_trade.append(f'</{tag}>')
            if tag == 'div':
                if self.depth == 0:
                    self.in_trade_item = False
                    self.trade_items.append(''.join(self.current_trade))
                    self.current_trade = []
                else:
                    self.depth -= 1
                    
        if tag == 'div' and self.in_timeline and not self.in_trade_item:
            # Check if we're ending the timeline container
            if self.depth == 0:
                self.in_timeline = False
                
    def handle_data(self, data):
        if self.in_trade_item:
            self.current_trade.append(data)

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
        
        # Path to original index.html (one level up from website/)
        self.original_index_path = self.base_path.parent / 'index.html'
        
        # Ensure dist directory exists
        self.dist_path.mkdir(exist_ok=True)
        
        # Component cache
        self.components = {}
        self.data = {}
        self.trade_items = []
        
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
        
    def get_team_names_from_trades(self, trade_items: List[str]) -> List[str]:
        """Extract unique team names from trade items"""
        team_names = set()
        
        for trade in trade_items:
            # Extract team names from trade summaries
            summary_match = re.search(r'<strong>([^<]+) ↔ ([^<]+)</strong>', trade)
            if summary_match:
                team_names.add(summary_match.group(1).strip())
                team_names.add(summary_match.group(2).strip())
                
        return sorted(list(team_names))
        
    def extract_trades_from_original(self):
        """Extract trade items from original index.html"""
        if not self.original_index_path.exists():
            print(f"Warning: Original index.html not found at {self.original_index_path}")
            return []
            
        with open(self.original_index_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract trade items using regex
        trade_pattern = r'<div class="trade-item">.*?</div></div></div>'
        self.trade_items = re.findall(trade_pattern, content, re.DOTALL)
        
        print(f"Extracted {len(self.trade_items)} trade items from original index.html")
        return self.trade_items
        
    def extract_javascript_data(self):
        """Extract JavaScript data variables from original index.html"""
        if not self.original_index_path.exists():
            return {}
            
        with open(self.original_index_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract key JavaScript data
        js_data = {}
        
        # Extract networkData
        network_match = re.search(r'const networkData = ({.*?});\s*(?:const|var|let|\n)', content, re.DOTALL)
        if network_match:
            js_data['networkData'] = network_match.group(1)
            
        # Extract draftData  
        draft_match = re.search(r'const draftData = ({.*?});\s*(?:const|var|let|\n)', content, re.DOTALL)
        if draft_match:
            js_data['draftData'] = draft_match.group(1)
            
        # Extract any other important data variables
        timeline_match = re.search(r'const timelineData = ({.*?});\s*(?:const|var|let|\n)', content, re.DOTALL)
        if timeline_match:
            js_data['timelineData'] = timeline_match.group(1)
            
        print(f"Extracted {len(js_data)} JavaScript data blocks")
        return js_data
        
    def extract_inline_scripts(self):
        """Extract inline scripts from original index.html"""
        if not self.original_index_path.exists():
            return []
            
        with open(self.original_index_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract all inline scripts except data definitions
        scripts = []
        script_pattern = r'<script[^>]*>\s*(?!const (?:networkData|draftData|timelineData))(.*?)</script>'
        matches = re.findall(script_pattern, content, re.DOTALL)
        
        for script in matches:
            script = script.strip()
            # Skip any script that defines our data variables
            if script and not any(script.startswith(f'const {var}') for var in ['networkData', 'draftData', 'timelineData']):
                # Also skip if it contains these definitions anywhere
                if not any(f'const {var} =' in script for var in ['networkData', 'draftData', 'timelineData']):
                    scripts.append(script)
                
        print(f"Extracted {len(scripts)} inline script blocks")
        return scripts
    
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
        
        # First, try to extract CSS from original index.html
        if self.original_index_path.exists():
            with open(self.original_index_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract all <style> blocks
            style_pattern = r'<style[^>]*>(.*?)</style>'
            style_matches = re.findall(style_pattern, content, re.DOTALL)
            
            if style_matches:
                combined_css.append("/* Extracted from original index.html */")
                for style in style_matches:
                    combined_css.append(style.strip())
        
        # Then add modular CSS files if they exist
        for css_file in css_files:
            css_path = self.styles_path / 'css' / css_file
            if css_path.exists():
                with open(css_path, 'r', encoding='utf-8') as f:
                    css_content = f.read().strip()
                    if css_content:
                        combined_css.append(f"\n/* {css_file} */\n{css_content}")
                
        return '\n\n'.join(combined_css)
        
    def combine_js(self) -> str:
        """Combine JavaScript modules and data into single script"""
        js_parts = []
        
        # First add the JavaScript data
        js_data = self.extract_javascript_data()
        if js_data:
            js_parts.append("// Data variables extracted from original")
            for var_name, var_data in js_data.items():
                js_parts.append(f"const {var_name} = {var_data};")
            js_parts.append("")
            
        # Don't add showPanel here - it's in EARLY_SCRIPTS now
        
        # Extract and add inline scripts from original
        inline_scripts = self.extract_inline_scripts()
        if inline_scripts:
            js_parts.append("// Inline scripts from original")
            js_parts.extend(inline_scripts)
            js_parts.append("")
        
        # Load modules in dependency order if they exist
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
        
        modules_found = False
        for js_file in module_order:
            js_path = self.js_path / js_file
            if js_path.exists():
                if not modules_found:
                    js_parts.append("// Modular JavaScript files")
                    modules_found = True
                    
                with open(js_path, 'r', encoding='utf-8') as f:
                    # Remove export/import statements for combined file
                    content = f.read()
                    content = re.sub(r'^export\s+', '', content, flags=re.MULTILINE)
                    content = re.sub(r'^import\s+.*?;?\s*$', '', content, flags=re.MULTILINE)
                    js_parts.append(f"// {js_file}\n{content}")
                
        return '\n\n'.join(js_parts)
        
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
        
        # Extract trade items from original
        trade_items = self.extract_trades_from_original()
        
        # Generate trade history HTML
        trade_history_html = '\n'.join(trade_items) if trade_items else '<!-- No trades found -->'
        
        # Calculate stats from trades
        total_trades = len(trade_items)
        
        # Load base template
        base_html = self.load_component('base.html')
        
        # Get team names for filter dropdown
        team_names = self.get_team_names_from_trades(trade_items)
        team_options = '\n'.join([f'<option value="{team}">{team}</option>' for team in team_names])
        
        # Generate draft year options with 2025 as default
        draft_year_options = """
                <option value="2025" selected>2025</option>
                <option value="2024">2024</option>
                <option value="2023">2023</option>
                <option value="2022">2022</option>
        """
        
        # Load all panel components
        panels_raw = {
            'OVERVIEW_PANEL': self.load_component('panels/overview.html'),
            'NETWORK_PANEL': self.load_component('panels/network.html'),
            'MATRIX_PANEL': self.load_component('panels/matrix.html'),
            'TIMELINE_PANEL': self.load_component('panels/timeline.html'),
            'PLAYERS_PANEL': self.load_component('panels/players.html'),
            'MATCHUPS_PANEL': self.load_component('panels/matchups.html'),
            'DRAFT_PANEL': self.load_component('panels/draft.html')
        }
        
        # Process timeline panel to inject trade history
        timeline_replacements = {
            'TRADE_HISTORY': trade_history_html,
            'TEAM_OPTIONS': team_options
        }
        panels_raw['TIMELINE_PANEL'] = self.replace_placeholders(panels_raw['TIMELINE_PANEL'], timeline_replacements)
        
        # Process draft panel to inject year options
        draft_replacements = {
            'DRAFT_YEAR_OPTIONS': draft_year_options,
            'DRAFT_DATA': '<!-- Draft data will be loaded dynamically -->'
        }
        panels_raw['DRAFT_PANEL'] = self.replace_placeholders(panels_raw['DRAFT_PANEL'], draft_replacements)
        
        panels = panels_raw
        
        # Load shared components
        shared = {
            'HEADER': self.load_component('header.html'),
            'CONTROLS': self.load_component('shared/controls.html'),
            'MODALS': self.load_component('shared/modals.html')
        }
        
        # Combine all CSS
        combined_css = self.combine_css()
        
        # Add critical CSS fix for panels
        panel_fix = """
        /* Critical panel display fix */
        .visualization-panel {
            display: none !important;
        }
        
        .visualization-panel.active {
            display: block !important;
        }
        """
        combined_css = combined_css + "\n" + panel_fix
        
        # Combine all JavaScript
        combined_js = self.combine_js()
        
        # Extract just the showPanel function to put early
        early_show_panel = """
<script>
// Define showPanel early so buttons work immediately
function showPanel(panelName) {
    try {
        console.log('showPanel called with:', panelName);
        
        // Check if DOM is ready
        if (document.readyState === 'loading') {
            console.log('DOM not ready, waiting...');
            document.addEventListener('DOMContentLoaded', function() {
                showPanel(panelName);
            });
            return;
        }
        
        // Get all panels
        const panels = document.querySelectorAll('.visualization-panel');
        console.log('Found panels:', panels.length);
        
        if (panels.length === 0) {
            console.error('No panels found! Looking for .visualization-panel');
            return;
        }
        
        // Hide all panels
        panels.forEach(panel => {
            panel.classList.remove('active');
            console.log('Hiding panel:', panel.id);
        });
        
        // Remove active class from all buttons
        document.querySelectorAll('.tab-button').forEach(button => {
            button.classList.remove('active');
        });
        
        // Show selected panel
        const targetPanel = document.getElementById(panelName + '-panel');
        if (targetPanel) {
            targetPanel.classList.add('active');
            console.log('Activated panel:', targetPanel.id);
        } else {
            console.error('Panel not found:', panelName + '-panel');
            console.log('Available panels:', Array.from(document.querySelectorAll('[id$="-panel"]')).map(p => p.id));
        }
        
        // Find and activate the corresponding button
        document.querySelectorAll('.tab-button').forEach(button => {
            if (button.textContent.toLowerCase().includes(panelName)) {
                button.classList.add('active');
            }
        });
    } catch (error) {
        console.error('Error in showPanel:', error);
    }
}

// Make it globally available
window.showPanel = showPanel;

// Add other missing global functions
function updateTradeGrade(tradeIndex, value) {
    console.log('updateTradeGrade called:', tradeIndex, value);
    // This will be overridden by the full implementation later
}

function showMatchupYear(year) {
    console.log('showMatchupYear called:', year);
    const yearSelect = document.getElementById('matchupYearSelect');
    if (yearSelect && !year) {
        year = yearSelect.value;
    }
    
    // Hide all year matchups
    document.querySelectorAll('.year-matchups').forEach(div => {
        div.style.display = 'none';
    });
    
    // Show selected year
    const targetYear = document.querySelector('.year-matchups[data-year="' + year + '"]');
    if (targetYear) {
        targetYear.style.display = 'block';
    }
}

function showDraftYear(year) {
    console.log('showDraftYear called:', year);
    const yearSelect = document.getElementById('draftYearSelect');
    if (yearSelect && !year) {
        year = yearSelect.value;
    }
    
    // Implementation will be loaded later
}

window.updateTradeGrade = updateTradeGrade;
window.showMatchupYear = showMatchupYear;
window.showDraftYear = showDraftYear;

// Debug on load
console.log('Core functions loaded: showPanel, updateTradeGrade, showMatchupYear, showDraftYear');
</script>
        """
        
        # Create replacements dictionary matching base.html template
        replacements = {
            'PAGE_TITLE': 'Eazy Pickens',
            'STYLES': f'<style>\n{combined_css}\n</style>',
            'EARLY_SCRIPTS': early_show_panel,  # Add showPanel early
            'SCRIPTS': '',  # Will be added after external scripts
            'HEADER_COMPONENT': shared.get('HEADER', ''),
            'CONTROLS_COMPONENT': shared.get('CONTROLS', ''),
            'OVERVIEW_PANEL': panels.get('OVERVIEW_PANEL', ''),
            'NETWORK_PANEL': panels.get('NETWORK_PANEL', ''),
            'MATRIX_PANEL': panels.get('MATRIX_PANEL', ''),
            'TIMELINE_PANEL': panels.get('TIMELINE_PANEL', ''),
            'PLAYERS_PANEL': panels.get('PLAYERS_PANEL', ''),
            'MATCHUPS_PANEL': panels.get('MATCHUPS_PANEL', ''),
            'DRAFT_PANEL': panels.get('DRAFT_PANEL', ''),
            'MODALS': shared.get('MODALS', ''),
            # These will be used within the panels
            'TOTAL_TRADES': str(total_trades),
            'TOTAL_PLAYERS': '234',  # These would need to be calculated from the data
            'TOTAL_PICKS': '87',    # These would need to be calculated from the data
            'TRADE_HISTORY': trade_history_html,
            'DRAFT_YEAR_OPTIONS': draft_year_options,
            'DRAFT_DATA': '<!-- Draft data will be loaded dynamically -->'
        }
        
        # Replace all placeholders
        final_html = self.replace_placeholders(base_html, replacements)
        
        # Add external script references if they exist in original
        if self.original_index_path.exists():
            with open(self.original_index_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
                
            # Extract external script references
            external_scripts = re.findall(r'<script[^>]*src="[^"]+"[^>]*></script>', original_content)
            if external_scripts:
                # Insert external scripts and then our combined JS before closing body tag
                scripts_html = '\n'.join(external_scripts) + f'\n<script>\n{combined_js}\n</script>'
                final_html = final_html.replace('</body>', scripts_html + '\n</body>')
        
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