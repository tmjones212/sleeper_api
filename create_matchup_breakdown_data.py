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

def load_api_cache(file_path: str) -> Dict[str, Any]:
    """Load and return API cache data to get league settings"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"API cache file not found: {file_path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing API cache JSON: {e}")
        return {}

def get_league_roster_positions(api_cache: Dict[str, Any], league_id: str) -> List[str]:
    """Get roster positions for the league from API cache"""
    league_data = api_cache.get(f"league_{league_id}", {})
    return league_data.get("roster_positions", [])

def get_player_name(player_id: str, players_data: Dict[str, Any]) -> str:
    """Get player name from player ID"""
    player = players_data.get(player_id, {})
    return player.get('full_name', f"Player {player_id}")

def get_player_position(player_id: str, players_data: Dict[str, Any]) -> str:
    """Get player position from player ID"""
    player = players_data.get(player_id, {})
    return player.get('position', 'UNK')

def convert_to_numbered_roster_positions(roster_positions: List[str]) -> List[str]:
    """Convert roster positions like ['QB', 'RB', 'RB', 'WR', 'WR'] to ['QB', 'RB1', 'RB2', 'WR1', 'WR2']"""
    position_counts = {}
    numbered_positions = []
    
    for position in roster_positions:
        if position == "BN":
            numbered_positions.append("BN")
            continue
            
        # Shorten position names
        if position == "SUPER_FLEX":
            position = "SF"
        elif position == "IDP_FLEX":
            position = "IDPF"
            
        # Count how many of this position we've seen
        position_counts[position] = position_counts.get(position, 0) + 1
        
        # Add number for positions that can have multiples
        if position in ['RB', 'WR', 'TE', 'FLEX', 'IDPF', 'LB', 'DB']:
            numbered_positions.append(f"{position}{position_counts[position]}")
        else:
            # QB, K, SF typically don't get numbered
            numbered_positions.append(position)
    
    return numbered_positions

def get_roster_slot_for_starter(starter_index: int, roster_positions: List[str]) -> str:
    """Get the roster slot for a starter based on their index in the starters array"""
    if starter_index < len(roster_positions):
        return roster_positions[starter_index]
    else:
        return f"FLEX{starter_index - len(roster_positions) + 1}"

def load_roster_to_team_mapping(api_cache: Dict[str, Any], league_id: str) -> Dict[int, str]:
    """Load roster to team name mapping from API cache"""
    users_key = f"https://api.sleeper.app/v1/league/{league_id}/users"
    rosters_key = f"https://api.sleeper.app/v1/league/{league_id}/rosters"
    
    users = api_cache.get(users_key, [])
    rosters = api_cache.get(rosters_key, [])
    
    roster_to_team = {}
    for roster in rosters:
        owner_id = roster.get('owner_id')
        roster_id = roster.get('roster_id')
        
        # Find the user with this owner_id
        team_name = None
        for user in users:
            if user.get('user_id') == owner_id:
                team_name = user.get('display_name', f'Team {roster_id}')
                break
        
        # Special cases for roster ownership issues
        if not team_name and roster_id == 9:
            if league_id == "1048308938824937472":  # 2024 league - caviar89
                caviar_user = next((u for u in users if u.get('user_id') == "1176293990462615552"), None)
                if caviar_user:
                    team_name = caviar_user.get('display_name', f'Team {roster_id}')
            # Add other special cases for different years if needed
        
        roster_to_team[roster_id] = team_name or f'Team {roster_id}'
    
    return roster_to_team

def process_matchup_breakdown(matchups_cache: Dict[str, Any], players_data: Dict[str, Any], api_cache: Dict[str, Any]) -> Dict[str, Any]:
    """Process matchup data to create detailed breakdowns with player names and positions"""
    
    processed_data = {}
    
    for cache_key, week_matchups in matchups_cache.items():
        if not isinstance(week_matchups, list):
            continue
            
        # Extract league ID from cache key (format: "league_id_week")
        league_id = cache_key.split('_')[0] if '_' in cache_key else None
        
        # Get league roster positions from API cache
        league_roster_positions = []
        roster_to_team_mapping = {}
        if league_id:
            league_roster_positions = get_league_roster_positions(api_cache, league_id)
            roster_to_team_mapping = load_roster_to_team_mapping(api_cache, league_id)
        
        # Convert to numbered positions (RB1, RB2, etc.)
        numbered_roster_positions = convert_to_numbered_roster_positions(league_roster_positions)
        
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
            
            # Process starters with correct roster positions
            starter_breakdown = []
            
            for i, player_id in enumerate(starters):
                roster_slot = get_roster_slot_for_starter(i, numbered_roster_positions)
                starter_breakdown.append({
                    'player_id': player_id,
                    'name': get_player_name(player_id, players_data),
                    'position': get_player_position(player_id, players_data),
                    'roster_slot': roster_slot,
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
                'bench_count': len(bench_players),
                'team_name': roster_to_team_mapping.get(roster_id, f'Team {roster_id}')
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
    api_cache_file = os.path.join(base_dir, "data", "api_cache.json")
    output_file = os.path.join(base_dir, "data", "matchup_breakdowns.json")
    
    print("Loading player data...")
    players_data = load_players_data(players_file)
    print(f"Loaded {len(players_data)} players")
    
    print("Loading matchups cache...")
    matchups_cache = load_matchups_cache(matchups_cache_file)
    print(f"Loaded {len(matchups_cache)} cached weeks")
    
    print("Loading API cache...")
    api_cache = load_api_cache(api_cache_file)
    print(f"Loaded API cache with {len(api_cache)} entries")
    
    print("Processing matchup breakdowns...")
    processed_data = process_matchup_breakdown(matchups_cache, players_data, api_cache)
    
    # Add metadata
    output_data = {
        'metadata': {
            'description': 'Preprocessed matchup breakdowns with player names and positions',
            'source_files': [players_file, matchups_cache_file, api_cache_file],
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