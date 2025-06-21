#!/usr/bin/env python3
"""
Component-based Update System
Allows updating specific parts of the website without touching others
Preserves custom code like Firebase integration and trade sliders
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

class ComponentUpdater:
    def __init__(self, website_path: str = None):
        """Initialize with paths and protected sections"""
        self.website_path = Path(website_path) if website_path else Path(__file__).parent.parent
        self.components_path = self.website_path / 'src' / 'components'
        self.data_path = self.website_path / 'src' / 'data'
        self.dist_path = self.website_path / 'dist'
        
        # Protected sections that should never be modified
        self.protected_sections = {
            'firebase': {
                'start': '<!-- FIREBASE_CONFIG_START -->',
                'end': '<!-- FIREBASE_CONFIG_END -->',
                'description': 'Firebase configuration and initialization'
            },
            'trade_sliders': {
                'start': '<!-- TRADE_SLIDERS_START -->',
                'end': '<!-- TRADE_SLIDERS_END -->',
                'description': 'Trade rating sliders functionality'
            },
            'custom_functions': {
                'start': '<!-- CUSTOM_FUNCTIONS_START -->',
                'end': '<!-- CUSTOM_FUNCTIONS_END -->',
                'description': 'Custom user-added functions'
            }
        }
        
        # Component mapping
        self.component_map = {
            'trades': {
                'template': 'trades/trade-item.html',
                'data_source': 'get_trades_data',
                'section_id': 'trade-history'
            },
            'network': {
                'template': 'panels/network.html',
                'data_source': 'get_network_data',
                'section_id': 'network-panel'
            },
            'matchups': {
                'template': 'panels/matchups.html',
                'data_source': 'get_matchups_data',
                'section_id': 'matchups-panel'
            },
            'draft': {
                'template': 'panels/draft.html',
                'data_source': 'get_draft_data',
                'section_id': 'draft-panel'
            },
            'overview': {
                'template': 'panels/overview.html',
                'data_source': 'get_overview_stats',
                'section_id': 'overview-panel'
            },
            'timeline': {
                'template': 'panels/timeline.html',
                'data_source': 'get_timeline_data',
                'section_id': 'timeline-panel'
            }
        }
        
    def preserve_protected_sections(self, content: str) -> Dict[str, str]:
        """Extract and preserve protected sections from content"""
        preserved = {}
        
        for section_name, markers in self.protected_sections.items():
            start_idx = content.find(markers['start'])
            end_idx = content.find(markers['end'])
            
            if start_idx != -1 and end_idx != -1:
                # Include the markers in the preserved content
                preserved[section_name] = content[start_idx:end_idx + len(markers['end'])]
                print(f"✓ Preserved {section_name}: {markers['description']}")
            else:
                print(f"⚠ Protected section '{section_name}' not found")
                
        return preserved
        
    def restore_protected_sections(self, content: str, preserved: Dict[str, str]) -> str:
        """Restore protected sections to the content"""
        for section_name, section_content in preserved.items():
            markers = self.protected_sections[section_name]
            
            # Find where to insert the protected content
            start_idx = content.find(markers['start'])
            end_idx = content.find(markers['end'])
            
            if start_idx != -1 and end_idx != -1:
                # Replace the section with preserved content
                content = (
                    content[:start_idx] + 
                    section_content + 
                    content[end_idx + len(markers['end']):]
                )
                print(f"✓ Restored {section_name}")
            else:
                # If markers not found, try to add them in appropriate place
                print(f"⚠ Could not find markers for {section_name}, attempting to add...")
                # This would need custom logic per section type
                
        return content
        
    def update_component(self, component_name: str, preserve_custom: bool = True):
        """Update a specific component while preserving custom code"""
        if component_name not in self.component_map:
            print(f"Error: Unknown component '{component_name}'")
            print(f"Available components: {', '.join(self.component_map.keys())}")
            return False
            
        component_info = self.component_map[component_name]
        
        # Read current index.html if it exists
        index_path = self.dist_path / 'index.html'
        preserved_sections = {}
        
        if index_path.exists() and preserve_custom:
            with open(index_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
            preserved_sections = self.preserve_protected_sections(current_content)
        
        # Load component template
        template_path = self.components_path / component_info['template']
        if not template_path.exists():
            print(f"Error: Template not found: {template_path}")
            return False
            
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
            
        # Get fresh data for the component
        try:
            # Import the appropriate service
            if component_name == 'trades':
                from transaction_service import TransactionService
                from client import SleeperAPI
                service = TransactionService(SleeperAPI())
                data = service.get_trades()  # Adjust parameters as needed
            elif component_name == 'network':
                from trade_visualization_service import LeagueVisualizationService
                from client import SleeperAPI
                service = LeagueVisualizationService(SleeperAPI())
                data = service.get_network_data()
            # Add more data sources as needed
            else:
                print(f"Data source for {component_name} not implemented yet")
                data = {}
        except Exception as e:
            print(f"Error getting data: {e}")
            data = {}
            
        # Process template with data
        processed_content = self.process_template(template_content, data)
        
        # Update the specific section in index.html
        if index_path.exists():
            with open(index_path, 'r', encoding='utf-8') as f:
                full_content = f.read()
                
            # Find and replace the component section
            section_id = component_info['section_id']
            pattern = rf'<div[^>]*id="{section_id}"[^>]*>.*?</div>(?=\s*<div[^>]*class="panel"|\s*</div>\s*<script|\s*$)'
            
            new_section = f'<div id="{section_id}" class="panel">\n{processed_content}\n</div>'
            full_content = re.sub(pattern, new_section, full_content, flags=re.DOTALL)
            
            # Restore protected sections
            if preserved_sections:
                full_content = self.restore_protected_sections(full_content, preserved_sections)
                
            # Write updated content
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(full_content)
                
            print(f"✓ Updated {component_name} component successfully")
            return True
        else:
            print("No index.html found. Run site_generator.py first.")
            return False
            
    def process_template(self, template: str, data: Any) -> str:
        """Process template with data"""
        # This is a simplified version - expand based on your needs
        if isinstance(data, dict):
            for key, value in data.items():
                template = template.replace(f"{{{{{key.upper()}}}}}", str(value))
        return template
        
    def update_trades_only(self):
        """Specialized method to update only trade data"""
        print("Updating trade data while preserving Firebase and sliders...")
        
        # Special handling for trades to ensure sliders are preserved
        index_path = self.dist_path / 'index.html'
        if not index_path.exists():
            print("Error: index.html not found")
            return
            
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract existing trade grades
        trade_grades = {}
        grade_pattern = r'<input[^>]*id="grade-(\d+)"[^>]*value="([^"]*)"'
        for match in re.finditer(grade_pattern, content):
            trade_id = match.group(1)
            grade_value = match.group(2)
            trade_grades[trade_id] = grade_value
            
        print(f"Preserved {len(trade_grades)} trade grades")
        
        # Update trades
        self.update_component('trades', preserve_custom=True)
        
        # Restore trade grades
        if trade_grades:
            with open(index_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for trade_id, grade_value in trade_grades.items():
                pattern = rf'(<input[^>]*id="grade-{trade_id}"[^>]*value=")[^"]*(")'
                content = re.sub(pattern, rf'\g<1>{grade_value}\g<2>', content)
                
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print(f"✓ Restored {len(trade_grades)} trade grades")
            
    def add_protected_section(self, section_name: str, content: str, 
                            insert_after: str = '</head>'):
        """Add a new protected section to the website"""
        if section_name in self.protected_sections:
            print(f"Protected section '{section_name}' already exists")
            return
            
        # Add to protected sections
        self.protected_sections[section_name] = {
            'start': f'<!-- {section_name.upper()}_START -->',
            'end': f'<!-- {section_name.upper()}_END -->',
            'description': f'User-added {section_name} section'
        }
        
        # Wrap content with markers
        wrapped_content = (
            f"\n{self.protected_sections[section_name]['start']}\n"
            f"{content}\n"
            f"{self.protected_sections[section_name]['end']}\n"
        )
        
        # Insert into index.html
        index_path = self.dist_path / 'index.html'
        if index_path.exists():
            with open(index_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
                
            # Insert after specified marker
            insert_idx = html_content.find(insert_after)
            if insert_idx != -1:
                insert_idx += len(insert_after)
                html_content = (
                    html_content[:insert_idx] + 
                    wrapped_content + 
                    html_content[insert_idx:]
                )
                
                with open(index_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                    
                print(f"✓ Added protected section '{section_name}'")
            else:
                print(f"Error: Could not find insertion point '{insert_after}'")
                

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Component-based website updater')
    parser.add_argument('component', nargs='?', help='Component to update')
    parser.add_argument('--list', action='store_true', help='List available components')
    parser.add_argument('--no-preserve', action='store_true', 
                       help='Do not preserve custom sections')
    parser.add_argument('--trades-only', action='store_true',
                       help='Update only trade data (preserves grades)')
    parser.add_argument('--add-protected', nargs=2, metavar=('NAME', 'FILE'),
                       help='Add a new protected section from file')
    
    args = parser.parse_args()
    
    updater = ComponentUpdater()
    
    if args.list:
        print("Available components:")
        for name, info in updater.component_map.items():
            print(f"  - {name}: {info['template']}")
    elif args.trades_only:
        updater.update_trades_only()
    elif args.add_protected:
        name, file_path = args.add_protected
        with open(file_path, 'r') as f:
            content = f.read()
        updater.add_protected_section(name, content)
    elif args.component:
        updater.update_component(args.component, preserve_custom=not args.no_preserve)
    else:
        parser.print_help()
        

if __name__ == '__main__':
    main()