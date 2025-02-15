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
		- Team name that made the pick
		- Player name that was picked
		- Pick number and round
		"""
		# Get the raw draft picks
		endpoint = f"{self.base_url}/draft/{draft_id}/picks"
		picks = self._make_request(endpoint)
		
		# Get the draft details to get league_id
		draft_details = self.get_draft_details(draft_id)
		league_id = draft_details['league_id']
		
		# Get team mapping
		teams = {team.user_id: team.display_name 
				for team in self.client.league_manager.get_league_users(league_id)}
		
		# Get number of teams in the draft
		teams_count = draft_details['settings']['teams']
		
		# Enhance each pick with additional information
		enhanced_picks = []
		for pick in picks:
			picked_player_id = pick.get('player_id')
			player_name = self.client.player_manager.get_player_name(picked_player_id)
			
			enhanced_pick = {
				'round': pick['round'],
				'pick_in_round': pick['pick_no'] - ((pick['round'] - 1) * teams_count),
				'overall_pick': pick['pick_no'],
				'team': teams.get(pick['picked_by'], 'Unknown Team'),
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
		print("Round | Pick | Overall | Team | Player | Position")
		print("-" * 70)
		
		for pick in picks:
			print(f"{pick['round']:5d} | {pick['pick_in_round']:4d} | {pick['overall_pick']:7d} | "
				  f"{pick['team']:<15} | {pick['player_name']:<20} | {pick['position']}")

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