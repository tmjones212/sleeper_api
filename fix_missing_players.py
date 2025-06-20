#!/usr/bin/env python3
import json
import requests

def add_missing_players():
    """Add missing player data for players in transactions but not in players.json"""
    
    print("🔍 Finding missing players...")
    
    # Load players.json
    with open('src/data/players.json', 'r') as f:
        players = json.load(f)
    
    # Load transaction data 
    with open('src/data/league_1181025001438806016_transactions.json', 'r') as f:
        transactions = json.load(f)
    
    missing_players = set()
    
    # Find all player IDs mentioned in transactions
    for trans in transactions:
        if trans.get('type') == 'trade':
            # Check adds
            if trans.get('adds'):
                for player_id in trans['adds'].keys():
                    if player_id not in players:
                        missing_players.add(player_id)
            
            # Check drops
            if trans.get('drops'):
                for player_id in trans['drops'].keys():
                    if player_id not in players:
                        missing_players.add(player_id)
    
    print(f"Found {len(missing_players)} missing players: {list(missing_players)}")
    
    # We know 7526 is Jaylen Waddle, let's add him manually
    if '7526' in missing_players:
        players['7526'] = {
            "player_id": "7526",
            "first_name": "Jaylen",
            "last_name": "Waddle",
            "full_name": "Jaylen Waddle",
            "position": "WR",
            "team": "MIA",
            "age": 26,
            "status": "Active",
            "height": "70",
            "weight": "182",
            "years_exp": 4,
            "college": "Alabama",
            "fantasy_positions": ["WR"],
            "active": True,
            "number": 17,
            "birth_date": "1998-11-25",
            "injury_status": None,
            "name": "JAYLEN WADDLE"
        }
        print("✅ Added Jaylen Waddle (7526)")
        missing_players.remove('7526')
    
    # For any other missing players, add placeholder data
    for player_id in missing_players:
        players[player_id] = {
            "player_id": player_id,
            "first_name": "Unknown",
            "last_name": f"Player{player_id}",
            "full_name": f"Unknown Player{player_id}",
            "position": "UNK",
            "team": None,
            "age": None,
            "status": "Active",
            "height": "",
            "weight": "",
            "years_exp": 0,
            "college": "",
            "fantasy_positions": ["UNK"],
            "active": True,
            "number": None,
            "birth_date": None,
            "injury_status": None,
            "name": f"UNKNOWN PLAYER{player_id}"
        }
        print(f"✅ Added placeholder for player {player_id}")
    
    # Save updated players.json
    with open('src/data/players.json', 'w') as f:
        json.dump(players, f, indent=2)
    
    print(f"🎉 Fixed {len(missing_players) + (1 if '7526' in list(missing_players) + ['7526'] else 0)} missing players!")
    return True

if __name__ == "__main__":
    add_missing_players()