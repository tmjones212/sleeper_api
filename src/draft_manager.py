from typing import List, Dict, Any
from datetime import datetime

class DraftManager:
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
			league = self.client.league_manager.get_league(league_id, fetch_all=True)
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
		league = self.client.league_manager.get_league(league_id, fetch_all=True)
		
		# Create user_id to team name mapping
		user_id_to_team = {
			team.user_id: team.display_name 
			for team in league.teams
		}
		
		# Create roster_id to team name mapping
		roster_to_team = {
			team.roster.roster_id: team.display_name 
			for team in league.teams 
			if team.roster
		}
		
		# Create position to team name mapping
		position_to_team = {}
		for user_id, position in draft_order.items():
			team_name = user_id_to_team.get(user_id)
			if team_name:
				position_to_team[position] = team_name
		
		# Debug print
		print("\nDraft Position to Team Mapping:")
		for pos, team in position_to_team.items():
			print(f"Position {pos}: {team}")
		
		enhanced_picks = []
		teams_count = len(draft_order)
		
		for pick in picks:
			picked_player_id = pick.get('player_id')
			player_name = self.client.player_manager.get_player_name(picked_player_id)
			
			# Get the team that made the pick
			roster_id = pick.get('roster_id')
			picking_team = roster_to_team.get(roster_id, f"Team {pick.get('picked_by')}")
			
			# Get original owner based on draft position
			pick_number = pick['pick_no']
			draft_position = ((pick_number - 1) % teams_count) + 1  # Convert pick number to draft position
			original_owner = position_to_team.get(draft_position, f"Team {draft_position}")
			
			# Debug print for each pick
			print(f"\nPick {pick_number}:")
			print(f"Draft Position: {draft_position}")
			print(f"Original Owner: {original_owner}")
			
			enhanced_pick = {
				'round': pick['round'],
				'pick_in_round': pick['pick_no'] - ((pick['round'] - 1) * teams_count),
				'overall_pick': pick['pick_no'],
				'team': picking_team,
				'original_owner': original_owner,
				'player_name': player_name,
				'player_id': picked_player_id,
				'position': self.client.player_manager.get_player_position(picked_player_id),
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
		primary_name = self.client.team_manager.get_primary_name(username)
		if not primary_name:
			return []
		
		team_aliases = set(self.client.team_manager.get_all_aliases(primary_name))
		
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
		rosters = self.client.league_manager.get_league_rosters(league_id)
		roster_to_team = {}
		for roster in rosters:
			team = next((team for team in self.client.league_manager.get_league_users(league_id)
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

	def _make_request(self, endpoint: str) -> Any:
		"""Make a cached API request."""
		cache_key = endpoint
		cache = self.client.cache_manager.api_cache
		
		if cache_key in cache:
			return cache[cache_key]

		response = self.client.league_manager._make_request(endpoint)
		cache[cache_key] = response
		self.client.cache_manager.save_api_cache()
		
		return response 