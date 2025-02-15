import json
import os
import re
from typing import Dict
# from client import SleeperAPI
from models import Player
import requests
class PlayerManager:
    def __init__(self):
        self.players = self._load_players_from_file()
        self.base_url = "https://api.sleeper.app/v1"  # Could also pass this in from client

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