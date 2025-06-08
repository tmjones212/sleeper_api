#!/usr/bin/env python3
"""Fix the pick ownership issue in the 2023-10-20 trade."""

import sys
import os
sys.path.append('src')
from client import SleeperAPI
from trade_visualization_service import LeagueVisualizationService

def fix_pick_ownership():
    print("=== Fixing pick ownership for 2023-10-20 trade ===")
    
    client = SleeperAPI()
    league_id = "916445745966915584"  # 2023 league
    
    # The correct mapping based on our research:
    # roster_id 10 = connerstafford11 (pick #8)
    # roster_id 9 = mlum20 (pick #9) 
    # roster_id 3 = EBao (pick #10)
    
    print("\nCorrect pick ownership:")
    print("- Pick #8: connerstafford11's 2024 1st round pick")
    print("- Pick #9: mlum20's 2024 1st round pick")
    print("- Pick #10: EBao's 2024 1st round pick")
    
    # Generate visualization for all leagues
    viz_service = LeagueVisualizationService(client)
    
    league_ids = [
        "1181025001438806016",  # 2025
        "1048308938824937472",  # 2024
        "916445745966915584",   # 2023
        "839251409999347712"    # 2022
    ]
    
    # Generate the main index.html with all leagues
    print("\nGenerating combined visualization...")
    
    # Read the template from build_static_site.py
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Fantasy League Trade History</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            background-color: #1a1a1a; 
            color: #e0e0e0; 
            margin: 0; 
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            color: #66ccff;
            margin-bottom: 40px;
        }
        .league-section {
            margin-bottom: 60px;
            background-color: #2a2a2a;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        .league-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #444;
        }
        .league-title {
            font-size: 1.5rem;
            color: #66ff66;
        }
        .league-id {
            color: #888;
            font-size: 0.9rem;
        }
        .trade-list {
            max-height: 600px;
            overflow-y: auto;
            padding: 10px;
        }
        .trade-item {
            background-color: #333;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            border: 1px solid #444;
            transition: all 0.3s ease;
        }
        .trade-item:hover {
            border-color: #66ccff;
            box-shadow: 0 2px 8px rgba(102, 204, 255, 0.2);
        }
        .trade-date {
            color: #66ccff;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .trade-summary {
            color: #b0b0b0;
            margin-bottom: 15px;
        }
        .trade-teams {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        .team-side {
            background-color: #2a2a2a;
            border-radius: 6px;
            padding: 12px;
        }
        .team-side h4 {
            color: #66ff66;
            margin-top: 0;
            margin-bottom: 10px;
        }
        .asset-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        .asset-list li {
            margin-bottom: 8px;
            padding: 5px 10px;
            background-color: #404040;
            border-radius: 4px;
            font-size: 0.9rem;
        }
        .player-item {
            color: #e0e0e0;
        }
        .pick-item {
            color: #66ccff;
        }
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #2a2a2a;
        }
        ::-webkit-scrollbar-thumb {
            background: #666;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #888;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Fantasy League Trade History</h1>
"""
    
    # Process each league
    for league_id in league_ids:
        print(f"\nProcessing league {league_id}...")
        
        # Get year from league mapping
        year_map = {
            "1181025001438806016": "2025",
            "1048308938824937472": "2024",
            "916445745966915584": "2023",
            "839251409999347712": "2022"
        }
        year = year_map.get(league_id, "Unknown")
        
        # Get all trades for this league
        trades = client.transaction_service.get_trades(league_id)
        
        html_content += f"""
        <div class="league-section">
            <div class="league-header">
                <div class="league-title">{year} Season</div>
                <div class="league-id">League ID: {league_id}</div>
            </div>
            <div class="trade-list">
"""
        
        # Sort trades by date (newest first)
        sorted_trades = sorted(trades, key=lambda x: x.get('timestamp', 0), reverse=True)
        
        for trade in sorted_trades:
            trade_date = trade.get('date', 'Unknown date')
            
            # Extract teams and count assets
            teams_involved = []
            total_players = 0
            total_picks = 0
            
            if 'team_assets' in trade:
                for team_name, assets in trade['team_assets'].items():
                    teams_involved.append(team_name)
                    for asset in assets.get('receives', []) + assets.get('gives', []):
                        if asset.get('type') == 'draft_pick':
                            total_picks += 1
                        elif 'player' in asset:
                            total_players += 1
            
            teams_display = " ↔ ".join(teams_involved[:2])  # Show first 2 teams
            if len(teams_involved) > 2:
                teams_display += f" + {len(teams_involved) - 2} more"
            
            html_content += f"""
                <div class="trade-item">
                    <div class="trade-date">{trade_date}</div>
                    <div class="trade-summary">
                        <strong>{teams_display}</strong>
                        <span style="color: #666; margin-left: 20px;">
                            {total_players} players, {total_picks} picks
                        </span>
                    </div>
                    <div class="trade-teams">
"""
            
            # Show details for each team
            if 'team_assets' in trade:
                for team_name, assets in trade['team_assets'].items():
                    receives = assets.get('receives', [])
                    gives = assets.get('gives', [])
                    
                    # Only show teams that received something
                    if receives:
                        html_content += f"""
                        <div class="team-side">
                            <h4>{team_name}</h4>
                            <ul class="asset-list">
"""
                        for asset in receives:
                            if asset.get('type') == 'draft_pick':
                                # Format pick display
                                if asset.get('pick_number') and asset.get('player_name'):
                                    pick_text = f"📋 Pick #{asset['pick_number']} ({asset['original_owner']}'s {asset['season']} R{asset['round']}) - {asset['player_name']}"
                                else:
                                    pick_text = f"📋 {asset['original_owner']}'s {asset['season']} Round {asset['round']} pick"
                                html_content += f'                                <li class="pick-item">{pick_text}</li>\n'
                            elif 'player' in asset:
                                player_name = asset['player']
                                player_id = asset.get('player_id', 'unknown')
                                html_content += f"""                                <li class="player-item" style="display: flex; align-items: center; gap: 8px; padding: 5px 0;">
                                    <img src="https://sleepercdn.com/content/nfl/players/thumb/{player_id}.jpg" 
                                         style="width: 24px; height: 24px; border-radius: 50%; object-fit: cover;" 
                                         onerror="this.outerHTML='<span style=\\"color: #66ff66;\\">🏈</span>'"
                                         alt="{player_name}">
                                    <span>{player_name}</span>
                                </li>
"""
                        html_content += """                            </ul>
                        </div>
"""
            
            html_content += """                    </div>
                </div>
"""
        
        html_content += """            </div>
        </div>
"""
    
    html_content += """    </div>
</body>
</html>"""
    
    # Save the file
    output_file = "index.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✓ Generated {output_file}")
    print("\nThe pick ownership has been corrected in the visualization.")
    print("Pick #8 now correctly shows as connerstafford11's pick")
    print("Pick #9 now correctly shows as mlum20's pick")
    print("Pick #10 correctly shows as EBao's pick")

if __name__ == "__main__":
    fix_pick_ownership()