from typing import List, Dict, Any
from datetime import datetime

class DraftManager:
	def __init__(self, client):
		self.client = client
		self.base_url = "https://api.sleeper.app/v1"

	def get_league_drafts(self, league_id: str) -> List[Dict[str, Any]]:
		"""Get all drafts for a league."""
		endpoint = f"{self.base_url}/league/{league_id}/drafts"
		response = self._make_request(endpoint)
		return response

	def get_draft_picks(self, draft_id: str) -> List[Dict[str, Any]]:
		"""
		Get all picks for a draft with enhanced information including:
		- Team that made the pick
		- Original owner of the pick
		- Player name that was picked
		- Pick number and round
		"""
		# Get the raw draft picks
		endpoint = f"{self.base_url}/draft/{draft_id}/picks"
		picks = self._make_request(endpoint)
		
		# Get the draft details to get league_id and slot_to_roster_id mapping
		draft_details = self.get_draft_details(draft_id)
		league_id = draft_details['league_id']
		slot_to_roster_id = draft_details.get('slot_to_roster_id', {})
		
		# Get traded picks during the draft
		traded_picks = self.get_traded_picks(draft_id)
		
		# Get team mapping
		teams = {team.user_id: team.display_name 
				for team in self.client.league_manager.get_league_users(league_id)}
		
		# Create roster_id to team name mapping
		rosters = self.client.league_manager.get_league_rosters(league_id)
		roster_to_team = {}
		for roster in rosters:
			team = next((team for team in self.client.league_manager.get_league_users(league_id) 
						if team.user_id == roster.owner_id), None)
			if team:
				roster_to_team[roster.roster_id] = team.display_name
		
		# Get number of teams in the draft
		teams_count = draft_details['settings']['teams']
		
		# Enhance each pick with additional information
		enhanced_picks = []
		for pick in picks:
			picked_player_id = pick.get('player_id')
			player_name = self.client.player_manager.get_player_name(picked_player_id)
			
			# Determine original owner based on draft slot
			pick_slot = pick.get('draft_slot')
			original_roster_id = slot_to_roster_id.get(str(pick_slot))
			original_owner = roster_to_team.get(original_roster_id, 'Unknown Team')
			
			# Check if this pick was traded
			pick_key = f"{pick['round']}.{original_roster_id}"
			if pick_key in traded_picks:
				original_owner = traded_picks[pick_key]['from_team']
			
			enhanced_pick = {
				'round': pick['round'],
				'pick_in_round': pick['pick_no'] - ((pick['round'] - 1) * teams_count),
				'overall_pick': pick['pick_no'],
				'team': teams.get(pick['picked_by'], 'Unknown Team'),
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