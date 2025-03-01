import os
import json
import re
import requests
from typing import List, Dict, Any
from datetime import datetime
from bs4 import BeautifulSoup

class KTCService:
    def __init__(self):
        self.cache_dir = "cache"
        # Create cache directory if it doesn't exist
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def get_player_values(self) -> List[Dict[str, Any]]:
        """Get current player values from KeepTradeCut with caching."""
        # Define cache file path
        today = datetime.now().strftime('%Y%m%d')
        cache_file = os.path.join(self.cache_dir, f'ktc_values_{today}.json')
        
        # Check if we have cached data from today
        if os.path.exists(cache_file):
            print(f"Loading KTC values from cache: {cache_file}")
            with open(cache_file, 'r') as f:
                return json.load(f)
        
        # If no cache, fetch new data
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
        }
        
        try:
            # Get player data from the rankings page
            rankings_url = "https://keeptradecut.com/dynasty-rankings"
            response = requests.get(rankings_url, headers=headers)
            response.raise_for_status()
            
            # Find the playersArray in the JavaScript
            # Extract the players array from the JavaScript
            players_match = re.search(r'var playersArray = (\[.*?\]);', response.text, re.DOTALL)
            if not players_match:
                print("Could not find players array in response")
                return []
                
            players_json = players_match.group(1)
            players_data = json.loads(players_json)
            
            # Convert to our format
            players = []
            for player in players_data:
                # Get superflex value by default
                value = player.get('superflexValues', {}).get('value', 0)
                
                players.append({
                    'id': player['playerID'],
                    'name': player['playerName'],
                    'player_name': player['playerName'],  # For compatibility with existing code
                    'value': value
                })
                
                # Debug output for first few players
                if len(players) < 3:
                    print(f"Added player: {player['playerName']} (ID: {player['playerID']}, Value: {value})")
            
            print(f"Total players processed: {len(players)}")
            
            # Save to cache
            print(f"Saving KTC values to cache: {cache_file}")
            with open(cache_file, 'w') as f:
                json.dump(players, f, indent=2)
            
            return players
            
        except requests.RequestException as e:
            print(f"Error fetching KTC data: {str(e)}")
            return []
        except Exception as e:
            print(f"Unexpected error processing KTC data: {str(e)}")
            print(f"Error details: {type(e).__name__}: {str(e)}")
            return []
    
    def get_draft_pick_ids(self) -> Dict[int, str]:
        """Get KTC IDs and names for draft picks."""
        url = "https://keeptradecut.com/dynasty-rankings?page=0&filters=RDP"
        
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        ktc_id_to_pick = {}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Use BeautifulSoup to parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all elements with class 'player-name'
            player_nodes = soup.find_all(class_='player-name')
            
            for node in player_nodes:
                # Extract player name and clean it
                pick_name = node.get_text().strip().replace('FA', '')
                print(f"PickName: {pick_name}")
                
                # Find the anchor tag and extract the href
                href_node = node.find('a')
                if href_node and href_node.get('href'):
                    href = href_node['href'].strip()
                    
                    # Extract the ID using regex
                    match = re.search(r'\d+$', href)
                    if match:
                        ktc_id = int(match.group())
                        ktc_id_to_pick[ktc_id] = pick_name
                        print(f"KeepTradeCutId: {ktc_id}")
                    else:
                        print("No KeepTradeCutId found in href.")
                else:
                    print("No href found for this player.")
            
            # Print the dictionary for debugging
            for ktc_id, name in ktc_id_to_pick.items():
                print(f"Key = {ktc_id}, Value = {name}")
                
            return ktc_id_to_pick
            
        except requests.RequestException as e:
            print(f"Error fetching KTC draft pick data: {str(e)}")
            return {} 