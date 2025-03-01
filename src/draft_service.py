from typing import List, Dict, Any
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re
import json
import os

from player_extensions import format_name

class DraftService:
	def __init__(self, client):
		self.client = client
		self.base_url = "https://api.sleeper.app/v1"

	def get_league_drafts(self, league_id: str) -> List[Dict[str, Any]]:
		"""Get all drafts for a league."""
		endpoint = f"{self.base_url}/league/{league_id}/drafts"
		drafts = self._make_request(endpoint)
		
		# For each draft, get and process the draft details
		for draft in drafts:
			draft_id = draft['draft_id']
			draft_details = self.get_draft_details(draft_id)
			
			# Print draft order information for debugging
			print(f"\nDraft Order for draft {draft_id}:")
			draft_order = draft_details.get('draft_order', {})
			
			# Get league data to map user IDs to team names
			league = self.client.league_service.get_league(league_id, fetch_all=True)
			user_id_to_team = {
				team.user_id: team.display_name 
				for team in league.teams
			}
			
			print("\nDraft Order Mapping:")
			for user_id, position in draft_order.items():
				team_name = user_id_to_team.get(user_id, f"Unknown Team ({user_id})")
				print(f"Position {position}: {team_name} (User ID: {user_id})")
			
			# Store the processed draft order in the draft object
			draft['processed_draft_order'] = {
				position: user_id_to_team.get(user_id, f"Team {position}")
				for user_id, position in draft_order.items()
			}
		
		return drafts

	def get_draft_picks(self, draft_id: str) -> List[Dict[str, Any]]:
		"""Get all picks for a draft with enhanced information."""
		endpoint = f"{self.base_url}/draft/{draft_id}/picks"
		picks = self._make_request(endpoint)
		
		# Get the draft details
		draft_details = self.get_draft_details(draft_id)
		league_id = draft_details['league_id']
		draft_order = draft_details.get('draft_order', {})
		
		# Get league data
		league = self.client.league_service.get_league(league_id, fetch_all=True)
		
		# Create mappings...
		user_id_to_team = {team.user_id: team.display_name for team in league.teams}
		roster_to_team = {team.roster.roster_id: team.display_name for team in league.teams if team.roster}
		position_to_team = {position: user_id_to_team.get(user_id) 
						   for user_id, position in draft_order.items() 
						   if user_id_to_team.get(user_id)}
		
		enhanced_picks = []
		teams_count = len(draft_order)
		
		# Get KTC data once for all picks
		ktc_data = self.get_ktc_player_value()
		print("\nDEBUG: First few KTC players:")
		for player in ktc_data[:5]:
			print(f"KTC Player: {player.get('player_name', 'NO NAME')} - Value: {player.get('value', 'NO VALUE')}")
		
		print("\nDraft Picks:")
		print("-" * 80)
		
		for pick in picks:
			picked_player_id = pick.get('player_id')
			player_name = self.client.player_service.get_player_name(picked_player_id)
			player_position = self.client.player_service.get_player_position(picked_player_id)
			
			# Get KTC value for the player with debug logging
			ktc_value = None
			if picked_player_id:
				print(f"\nDEBUG: Looking for KTC value for {player_name}")
				for ktc_player in ktc_data:
					ktc_player_name = ktc_player.get('player_name', '')
					print(f"Comparing with KTC player: {ktc_player_name}")
					if self._match_player_name(ktc_player_name, player_name):
						ktc_value = ktc_player.get('value', 0)
						print(f"Found match! KTC value: {ktc_value}")
						break
				if ktc_value is None:
					print(f"No KTC match found for {player_name}")
			
			# Rest of the pick processing...
			roster_id = pick.get('roster_id')
			picking_team = roster_to_team.get(roster_id, f"Team {pick.get('picked_by')}")
			
			pick_number = pick['pick_no']
			draft_position = ((pick_number - 1) % teams_count) + 1
			original_owner = position_to_team.get(draft_position, f"Team {draft_position}")
			
			pick_in_round = pick['pick_no'] - ((pick['round'] - 1) * teams_count)
			formatted_pick = f"{pick['round']}.{pick_in_round:02d}"
			
			enhanced_pick = {
				'round': pick['round'],
				'pick_in_round': pick_in_round,
				'overall_pick': pick['pick_no'],
				'team': picking_team,
				'original_owner': original_owner,
				'player_name': player_name,
				'player_id': picked_player_id,
				'position': player_position,
				'ktc_value': ktc_value,
				'image_url': self.client.player_service.get_player_image_url(picked_player_id)
			}
			enhanced_picks.append(enhanced_pick)
		
		return enhanced_picks

	def get_draft_details(self, draft_id: str) -> Dict[str, Any]:
		"""Get detailed information about a specific draft."""
		endpoint = f"{self.base_url}/draft/{draft_id}"
		return self._make_request(endpoint)

	def print_draft_picks(self, draft_id: str):
		"""Print draft picks in a readable format."""
		picks = self.get_draft_picks(draft_id)
		
		print("\nDraft Results:")
		print("Round | Pick | Overall | Team | Original Owner | Player | Position")
		print("-" * 90)
		
		for pick in picks:
			print(f"{pick['round']:5d} | {pick['pick_in_round']:4d} | {pick['overall_pick']:7d} | "
				  f"{pick['team']:<15} | {pick['original_owner']:<15} | "
				  f"{pick['player_name']:<20} | {pick['position']}")

	def get_user_draft_picks(self, draft_id: str, username: str) -> List[Dict[str, Any]]:
		"""Get all picks made by a specific user in a draft."""
		all_picks = self.get_draft_picks(draft_id)
		
		# Get the primary team name and all aliases
		primary_name = self.client.team_service.get_primary_name(username)
		if not primary_name:
			return []
		
		team_aliases = set(self.client.team_service.get_all_aliases(primary_name))
		
		# Filter picks for the specified user (checking against all aliases)
		user_picks = [
			pick for pick in all_picks 
			if pick['team'].lower() in team_aliases
		]
		
		return user_picks

	def get_traded_picks(self, draft_id: str) -> Dict[str, Dict[str, str]]:
		"""Get all traded picks in a draft."""
		endpoint = f"{self.base_url}/draft/{draft_id}/traded_picks"
		traded_picks_data = self._make_request(endpoint)
		
		# Get draft details to get league_id
		draft_details = self.get_draft_details(draft_id)
		league_id = draft_details['league_id']
		
		# Get roster_id to team name mapping
		rosters = self.client.league_service.get_league_rosters(league_id)
		roster_to_team = {}
		for roster in rosters:
			team = next((team for team in self.client.league_service.get_league_users(league_id)
						if team.user_id == roster.owner_id), None)
			if team:
				roster_to_team[roster.roster_id] = team.display_name
		
		# Create a lookup dictionary to track the earliest owner of each pick
		pick_ownership = {}  # Format: {pick_key: {'earliest_owner': id, 'current_owner': id}}
		
		# Sort trades by timestamp if available, otherwise assume they're in chronological order
		for trade in traded_picks_data:
			pick_key = f"{trade['round']}.{trade['roster_id']}"
			
			if pick_key not in pick_ownership:
				# First trade of this pick - previous_owner is the earliest owner
				pick_ownership[pick_key] = {
					'earliest_owner': trade['previous_owner_id'],
					'current_owner': trade['owner_id']
				}
			else:
				# Update only the current owner
				pick_ownership[pick_key]['current_owner'] = trade['owner_id']
		
		# Convert to the format expected by get_draft_picks
		traded_picks = {}
		for pick_key, ownership in pick_ownership.items():
			traded_picks[pick_key] = {
				'from_team': roster_to_team.get(ownership['earliest_owner'], 
											  f"Team {ownership['earliest_owner']}"),
				'to_team': roster_to_team.get(ownership['current_owner'], 
											f"Team {ownership['current_owner']}")
			}
		
		return traded_picks

	def print_picks(self, draft_id: str):
		"""Print all picks for a draft in a formatted way."""
		picks = self.get_draft_picks(draft_id)
		print("\nDraft Picks:")
		print("-" * 100)
		
		# Print column headers
		print(
			f"{'PICK':<5}"
			f"{'#':<4}"
			f"{'ORIGINAL OWNER':<22}"
			f"{'TEAM':<18}"
			f"{'PLAYER':<20}"
			f"{'POS'}"
		)
		print("-" * 100)
		
		for pick in picks:
			formatted_pick = f"{pick['round']}.{pick['pick_in_round']:02d}"
			print(
				f"{formatted_pick:<5}"  # e.g., "4.05"
				f"{pick['overall_pick']:<3} "  # e.g., "#35"
				f"orig: {pick['original_owner']:<16} "  # e.g., "orig: baodown"
				f"{pick['team']:<18}"  # e.g., "tmjones212"
				f"{pick['player_name']:<20}"  # e.g., "BROCK BOWERS"
				f"{pick['position']}"  # e.g., "TE"
			)
		print("-" * 100)

	def print_picks_csv(self, draft_id: str):
		"""Print all picks for a draft in CSV format."""
		picks = self.get_draft_picks(draft_id)
		
		# Print header
		print("PICK,#,ORIGINAL OWNER,TEAM,PLAYER,POS")
		
		# Print data
		for pick in picks:
			formatted_pick = f"{pick['round']}.{pick['pick_in_round']:02d}"
			print(
				f"{formatted_pick},"
				f"{pick['overall_pick']},"
				f"{pick['original_owner']},"
				f"{pick['team']},"
				f"{pick['player_name']},"
				f"{pick['position']}"
			)

	def _make_request(self, endpoint: str) -> Any:
		"""Make a cached API request."""
		cache_key = endpoint
		cache = self.client.cache_service.api_cache
		
		if cache_key in cache:
			return cache[cache_key]

		response = self.client.league_service._make_request(endpoint)
		cache[cache_key] = response
		self.client.cache_service.save_api_cache()
		
		return response 

	def get_ktc_player_value(self) -> List[Dict[str, Any]]:
		"""Get current player values from KeepTradeCut with caching."""
		# Define cache file path
		cache_dir = "cache"
		today = datetime.now().strftime('%Y%m%d')
		cache_file = os.path.join(cache_dir, f'ktc_values_{today}.json')
		
		# Create cache directory if it doesn't exist
		if not os.path.exists(cache_dir):
			os.makedirs(cache_dir)
		
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

	def get_draft_pick_ktc_ids(self) -> Dict[int, str]:
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

	def enhance_draft_picks_with_ktc(self, picks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
		"""Add KTC values to draft picks data."""
		ktc_data = self.get_ktc_player_value()
		ktc_pick_ids = self.get_draft_pick_ktc_ids()
		
		# Create reverse lookup from pick name to KTC ID
		pick_name_to_ktc_id = {name.upper(): ktc_id for ktc_id, name in ktc_pick_ids.items()}
		
		for pick in picks:
			player_id = pick.get('player_id')
			if player_id:
				# Try to find matching player in KTC data
				ktc_value = next(
					(p.get('value', 0) for p in ktc_data 
					 if self._match_player_name(p.get('name', ''), pick.get('player_name', ''))),
					0
				)
				pick['ktc_value'] = ktc_value
				
				# If it's a draft pick, also try to match by pick name
				if not ktc_value and pick.get('player_name', '').upper().startswith('20'):
					pick_name = pick.get('player_name', '').upper()
					if pick_name in pick_name_to_ktc_id:
						ktc_id = pick_name_to_ktc_id[pick_name]
						ktc_value = next(
							(p.get('value', 0) for p in ktc_data if p.get('id') == ktc_id),
							0
						)
						pick['ktc_value'] = ktc_value
		
		return picks

	def _match_player_name(self, ktc_name: str, sleeper_name: str) -> bool:
		"""Match player names between KTC and Sleeper formats."""
		ktc_name = self.client.player_service.format_player_name(ktc_name)
		sleeper_name = self.client.player_service.format_player_name(sleeper_name)
		return ktc_name == sleeper_name 