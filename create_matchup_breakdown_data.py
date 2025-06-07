#!/usr/bin/env python3
"""
Create a preprocessed JSON file with matchup breakdowns including player names and roster positions.
This combines data from matchups_cache.json and players.json for easier frontend display.
"""

import json
import os
from typing import Dict, List, Any, Optional

def load_players_data(file_path: str) -> Dict[str, Any]:
    """Load and return player data from players.json"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Players file not found: {file_path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing players JSON: {e}")
        return {}

def load_matchups_cache(file_path: str) -> Dict[str, Any]:
    """Load and return matchup data from matchups_cache.json"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Matchups cache file not found: {file_path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing matchups cache JSON: {e}")
        return {}

def get_player_name(player_id: str, players_data: Dict[str, Any]) -> str:
    """Get player name from player ID"""
    player = players_data.get(player_id, {})
    return player.get('full_name', f"Player {player_id}")

def get_player_position(player_id: str, players_data: Dict[str, Any]) -> str:
    """Get player position from player ID"""
    player = players_data.get(player_id, {})
    return player.get('position', 'UNK')

def infer_roster_position(player_id: str, starters: List[str], players_data: Dict[str, Any], league_roster_positions: List[str]) -> str:
    """Infer the roster position (QB1, RB1, etc.) based on starter order and position"""
    if player_id not in starters:
        return "BN"  # Bench
    
    starter_index = starters.index(player_id)
    player_position = get_player_position(player_id, players_data)
    
    # Map to standard fantasy positions if we have roster position info
    if starter_index < len(league_roster_positions):
        return league_roster_positions[starter_index]
    
    # Fallback: create position based on player position and index
    position_counts = {}
    for i, pid in enumerate(starters[:starter_index + 1]):
        pos = get_player_position(pid, players_data)
        position_counts[pos] = position_counts.get(pos, 0) + 1
    
    current_count = position_counts.get(player_position, 1)
    
    # Return numbered position
    if player_position in ['QB', 'K', 'DEF']:
        return player_position
    elif player_position in ['RB', 'WR', 'TE']:
        return f"{player_position}{current_count}"
    else:
        return f"FLEX{current_count}"

def process_matchup_breakdown(matchups_cache: Dict[str, Any], players_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process matchup data to create detailed breakdowns with player names and positions"""
    
    processed_data = {}
    
    for cache_key, week_matchups in matchups_cache.items():
        if not isinstance(week_matchups, list):
            continue
            
        processed_week = []
        
        for matchup in week_matchups:
            if not isinstance(matchup, dict):
                continue
                
            # Extract basic matchup info
            roster_id = matchup.get('roster_id')
            total_points = matchup.get('points', 0)
            matchup_id = matchup.get('matchup_id')
            starters = matchup.get('starters', [])
            all_players = matchup.get('players', [])
            players_points = matchup.get('players_points', {})
            
            # Calculate starter points
            starter_points = sum(players_points.get(pid, 0) for pid in starters)
            bench_points = total_points - starter_points
            
            # Process starters with positions
            starter_breakdown = []
            # Assume standard positions - you might want to get this from league data
            roster_positions = ['QB', 'RB1', 'RB2', 'WR1', 'WR2', 'WR3', 'TE', 'FLEX', 'K', 'DEF']
            
            for i, player_id in enumerate(starters):
                position = roster_positions[i] if i < len(roster_positions) else f"FLEX{i-7}"
                starter_breakdown.append({
                    'player_id': player_id,
                    'name': get_player_name(player_id, players_data),
                    'position': get_player_position(player_id, players_data),
                    'roster_slot': position,
                    'points': players_points.get(player_id, 0)
                })
            
            # Process bench players
            bench_players = [pid for pid in all_players if pid not in starters]
            bench_breakdown = []
            
            for player_id in bench_players:
                bench_breakdown.append({
                    'player_id': player_id,
                    'name': get_player_name(player_id, players_data),
                    'position': get_player_position(player_id, players_data),
                    'roster_slot': 'BN',
                    'points': players_points.get(player_id, 0)
                })
            
            # Sort bench by points descending
            bench_breakdown.sort(key=lambda x: x['points'], reverse=True)
            
            # Create processed matchup
            processed_matchup = {
                'roster_id': roster_id,
                'matchup_id': matchup_id,
                'total_points': total_points,
                'starter_points': starter_points,
                'bench_points': bench_points,
                'starters': starter_breakdown,
                'bench': bench_breakdown,
                'all_players_count': len(all_players),
                'starters_count': len(starters),
                'bench_count': len(bench_players)
            }
            
            processed_week.append(processed_matchup)
        
        processed_data[cache_key] = processed_week
    
    return processed_data

def main():
    """Main function to create the preprocessed matchup breakdown data"""
    
    # File paths
    base_dir = "/home/alaba/coolProjects"
    players_file = os.path.join(base_dir, "data", "players.json")
    matchups_cache_file = os.path.join(base_dir, "data", "matchups_cache.json")
    output_file = os.path.join(base_dir, "data", "matchup_breakdowns.json")
    
    print("Loading player data...")
    players_data = load_players_data(players_file)
    print(f"Loaded {len(players_data)} players")
    
    print("Loading matchups cache...")
    matchups_cache = load_matchups_cache(matchups_cache_file)
    print(f"Loaded {len(matchups_cache)} cached weeks")
    
    print("Processing matchup breakdowns...")
    processed_data = process_matchup_breakdown(matchups_cache, players_data)
    
    # Add metadata
    output_data = {
        'metadata': {
            'description': 'Preprocessed matchup breakdowns with player names and positions',
            'source_files': [players_file, matchups_cache_file],
            'total_weeks_processed': len(processed_data),
            'created_by': 'create_matchup_breakdown_data.py'
        },
        'matchups': processed_data
    }
    
    print(f"Writing processed data to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print("✅ Matchup breakdown data created successfully!")
    print(f"📁 File saved: {output_file}")
    
    # Print sample data for verification
    if processed_data:
        sample_key = list(processed_data.keys())[0]
        sample_matchup = processed_data[sample_key][0] if processed_data[sample_key] else None
        
        if sample_matchup:
            print(f"\n📊 Sample data from {sample_key}:")
            print(f"   Roster ID: {sample_matchup['roster_id']}")
            print(f"   Total Points: {sample_matchup['total_points']}")
            print(f"   Starters: {sample_matchup['starters_count']}")
            print(f"   Bench: {sample_matchup['bench_count']}")
            
            if sample_matchup['starters']:
                print(f"   Top starter: {sample_matchup['starters'][0]['name']} ({sample_matchup['starters'][0]['points']} pts)")
            
            if sample_matchup['bench']:
                print(f"   Top bench: {sample_matchup['bench'][0]['name']} ({sample_matchup['bench'][0]['points']} pts)")

if __name__ == "__main__":
    main()