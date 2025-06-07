#!/usr/bin/env python3
"""
Build static HTML files for GitHub Pages deployment
"""
import os
import sys
sys.path.append('src')
from client import SleeperAPI
from trade_visualization_service import LeagueVisualizationService

def build_static_site():
    """Generate static HTML files for all leagues"""
    client = SleeperAPI()
    service = LeagueVisualizationService(client)
    
    # Your league IDs
    league_ids = [
        "1181025001438806016",  # 2025
        "1048308938824937472",  # 2024
        "916445745966915584",   # 2023
        "839251409999347712"    # 2022
    ]
    
    # Create docs directory for GitHub Pages
    docs_dir = "docs"
    os.makedirs(docs_dir, exist_ok=True)
    
    # Generate HTML for each league
    for league_id in league_ids:
        try:
            print(f"Generating visualization for league {league_id}...")
            html_content = service.generate_league_visualization_html(league_id)
            
            # Save to docs directory
            output_file = os.path.join(docs_dir, f"league_{league_id}.html")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✓ Generated {output_file}")
            
        except Exception as e:
            print(f"✗ Error generating league {league_id}: {e}")
    
    # Create index.html with links to all leagues
    index_content = """<!DOCTYPE html>
<html>
<head>
    <title>Fantasy League Visualizations</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        .league-link { display: block; padding: 15px; margin: 10px 0; background: #f5f5f5; text-decoration: none; color: #333; border-radius: 5px; }
        .league-link:hover { background: #e5e5e5; }
    </style>
</head>
<body>
    <h1>Fantasy League Visualizations</h1>
    <p>Select a league to view its complete analysis including trades, drafts, and matchups:</p>
    
    <a href="league_1181025001438806016.html" class="league-link">
        <strong>2025 League</strong><br>
        League ID: 1181025001438806016
    </a>
    
    <a href="league_1048308938824937472.html" class="league-link">
        <strong>2024 League</strong><br>
        League ID: 1048308938824937472
    </a>
    
    <a href="league_916445745966915584.html" class="league-link">
        <strong>2023 League</strong><br>
        League ID: 916445745966915584
    </a>
    
    <a href="league_839251409999347712.html" class="league-link">
        <strong>2022 League</strong><br>
        League ID: 839251409999347712
    </a>
</body>
</html>"""
    
    index_file = os.path.join(docs_dir, "index.html")
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print(f"✓ Generated {index_file}")
    print(f"\nDone! Upload the '{docs_dir}' directory to GitHub Pages.")

if __name__ == "__main__":
    build_static_site()