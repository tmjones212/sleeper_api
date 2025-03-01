import json
import os
import re
from typing import Dict, List
# from client import SleeperAPI
from models import Player
import requests

class PlayerService:
    def __init__(self):
        self.base_url = "https://api.sleeper.app/v1"  # Could also pass this in from client
        self.players = self._load_players_from_file()

    def _load_players_from_file(self, filename="data/players.json") -> Dict[str, Player]:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                print('loading players from file...')
                data = json.load(f)
            return {pid: Player(**player_data) for pid, player_data in data.items()}
        else:
            print(f"File {filename} not found. Fetching data from API...")
            return self.fetch_players_from_api()

    def fetch_players_from_api(self) -> Dict[str, Player]:
        url = f"{self.base_url}/players/nfl"
        print('getting players from api...')
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        players = {player_id: Player(**player_data) for player_id, player_data in data.items()}
        self._save_players_to_file(players)
        return players

    def _save_players_to_file(self, players: Dict[str, Player], filename="data/players.json"):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump({pid: {k: v for k, v in vars(p).items() if not k.startswith('_')} 
                      for pid, p in players.items()}, f)
        print(f"Players data saved to {filename}")

    def save_players_to_file(self, players: Dict[str, Player], filename="data/players.json"):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump({pid: {k: v for k, v in vars(p).items() if not k.startswith('_')} 
                      for pid, p in players.items()}, f)
        print(f"Players data saved to {filename}")

    def get_player_position(self, player_id: str) -> str:
        player = self.players.get(player_id)
        return player.position if player else "UNKNOWN"

    def get_player_name(self, player_id: str) -> str:
        player = self.players.get(player_id)
        return player.name if player else f"Unknown Player ({player_id})"

    @staticmethod
    def format_player_name(name: str) -> str:
        name = name.split('(')[0]  # Remove anything in parentheses
        name = name.strip().upper()
        name = re.sub(r'[,+.*]', '', name)
        name = re.sub(r'\s+(JR|SR|III|II|IV|V)$', '', name)
        name = name.replace("'", "").replace("-", " ")

        replacements = {
            "MITCHELL": "MITCH",
            "WILLIAM": "WILL",
            "BENJAMIN": "BEN",
            "MICHAEL": "MIKE",
            "JOSHUA": "JOSH",
            "ROBERT": "ROB",
            "CHRISTOPHER": "CHRIS",
            "KENNETH": "KEN",
            "JEFFREY": "JEFF",
            "GABRIEL": "GABE",
            "NATHANIEL": "NATE",
        }

        for old, new in replacements.items():
            name = name.replace(f"{old} ", f"{new} ")

        return name 

    def get_players(self, position: str = None, team: str = None, active: bool = True, search: str = None) -> List[Player]:
        """
        Get a filtered list of players.
        
        Args:
            position (str, optional): Filter by player position (e.g., "QB", "RB", "WR", etc.)
            team (str, optional): Filter by team (e.g., "LAR", "SF", etc.)
            active (bool, optional): Filter for active players only. Defaults to True.
            search (str, optional): Search player names (case-insensitive partial match)
        
        Returns:
            List[Player]: List of matching Player objects
        """
        filtered_players = []
        
        for player in self.players.values():
            # Skip inactive players if active flag is True
            if active and not player.active:
                continue
            
            # Apply position filter
            if position and player.position != position:
                continue
            
            # Apply team filter
            if team and player.team != team:
                continue
            
            # Apply name search
            if search:
                search_term = search.upper()
                player_name = self.format_player_name(f"{player.first_name} {player.last_name}")
                if search_term not in player_name:
                    continue
            
            filtered_players.append(player)
        
        # Sort players by name
        filtered_players.sort(key=lambda x: x.name)
        
        return filtered_players 

    def get_player_image_url(self, player_id: str) -> str:
        """
        Get the URL for a player's image from Sleeper CDN.
        
        Args:
            player_id (str): The player's ID
            
        Returns:
            str: The complete URL to the player's image on Sleeper CDN
        """
        return f"https://sleepercdn.com/content/nfl/players/{player_id}.jpg" 

    def get_player_age(self, player_id: str) -> int:
        """
        Get the age of a player.
        
        Args:
            player_id (str): The player's ID
            
        Returns:
            int: The player's age, or 0 if not found
        """
        player = self.players.get(player_id)
        if player and hasattr(player, 'age') and player.age:
            return player.age
        return 0 