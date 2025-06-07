import json
import os
import re
from typing import Any, Dict, List, Optional
import requests
from customer_json_encoder import CustomJSONEncoder
from exceptions import SleeperAPIException
from models import League, PlayerInfo, ProjectedStats, SleeperProjections, Team, Matchup, Player, Roster, PlayerProjection, PlayerStats
import csv
from datetime import datetime, timedelta
from cache_service import CacheService
from player_service import PlayerService
from season_service import SeasonService
from stats_service import StatsService
from matchup_service import MatchupService
from league_service import LeagueService
from projections_service import ProjectionsService
from transaction_service import TransactionService
from best_ball_service import BestBallService
from standings_service import StandingsService
from team_service import TeamService
from draft_service import DraftService
from trade_visualization_service import TradeVisualizationService

class SleeperAPI:
	BASE_URL = "https://api.sleeper.app/v1"

	def __init__(self, requested_league_id: str = None):
		self.requested_league_id = requested_league_id
		self.cache_service = CacheService()
		self.player_service = PlayerService()
		self.league_service = LeagueService(
			self.BASE_URL, 
			self.cache_service, 
			player_service=self.player_service
		)
		self.scoring_settings = self.league_service.scoring_settings
		self.season_service = SeasonService()
		self.stats_service = StatsService(self, self.cache_service, self.scoring_settings)
		self.matchup_service = MatchupService(self, self.cache_service)
		self.projections_service = ProjectionsService(self.cache_service)
		self.transaction_service = TransactionService(self)
		self.best_ball_service = BestBallService(self)
		self.standings_service = StandingsService(self)
		self.team_service = TeamService()
		self.draft_service = DraftService(self)
		self.trade_visualization_service = TradeVisualizationService(self)
		
		# Pre-load historical transactions into cache
		if len(self.cache_service.api_cache) == 0:  # Only load if cache is empty
			print("Loading historical transaction data...")
			current_league_id = "1048308938824937472"  # 2024 league
			self.transaction_service.get_all_historical_transactions(current_league_id)

		if self.requested_league_id:
			self.league_service.get_league(self.requested_league_id)

	def get_player_fields(self):
		url = f"{self.BASE_URL}/players/nfl"
		response = requests.get(url) 
		response.raise_for_status()
		data = response.json()
		first_player = next(iter(data.values()))
		print(json.dumps(first_player, indent=2))

	def print_team_fields(self, league_id: str):
		endpoint = f"{self.BASE_URL}/league/{league_id}/users"
		response = self._make_request(endpoint)
		if response and len(response) > 0:
			print(json.dumps(response[0], indent=2))
		else:
			print("No users found in the league or empty response.")
	
	def _make_request(self, endpoint: str) -> Dict[str, Any]:
		cache_key = endpoint
		if cache_key in self.cache_service.api_cache:
			return self.cache_service.api_cache[cache_key]

		response = requests.get(endpoint)
		if response.status_code == 200:
			data = response.json()
			self.cache_service.api_cache[cache_key] = data
			self.cache_service.save_api_cache()
			return data
		else:
			raise SleeperAPIException(f"API request failed: {response.status_code} - {response.text}")
	
	def generate_trade_visualization(self, league_id: str = None, output_file: str = None) -> str:
		"""Generate comprehensive trade visualization for a league"""
		target_league_id = league_id or self.requested_league_id
		if not target_league_id:
			raise ValueError("League ID must be provided either in constructor or as parameter")
		
		print(f"Generating trade visualization for league {target_league_id}...")
		output_path = self.trade_visualization_service.save_trade_visualization(
			target_league_id, output_file
		)
		print(f"Trade visualization saved to: {output_path}")
		return output_path
	
	def get_player_trade_journey(self, player_name: str, league_id: str = None) -> Dict[str, Any]:
		"""Get detailed trade journey for a specific player"""
		target_league_id = league_id or self.requested_league_id
		if not target_league_id:
			raise ValueError("League ID must be provided either in constructor or as parameter")
		
		return self.trade_visualization_service.get_player_trade_journey(target_league_id, player_name)
	
	def get_trade_network_analysis(self, league_id: str = None) -> Dict[str, Any]:
		"""Get trade network analysis for the league"""
		target_league_id = league_id or self.requested_league_id
		if not target_league_id:
			raise ValueError("League ID must be provided either in constructor or as parameter")
		
		return self.trade_visualization_service.get_trade_network_data(target_league_id)
