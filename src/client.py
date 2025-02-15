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
from cache_manager import CacheManager
from player_manager import PlayerManager
from season_manager import SeasonManager
from stats_manager import StatsManager
from matchup_manager import MatchupManager
from league_manager import LeagueManager
from projections_manager import ProjectionsManager
from transaction_manager import TransactionManager
from best_ball_manager import BestBallManager
from standings_manager import StandingsManager
from team_manager import TeamManager
from draft_manager import DraftManager

class SleeperAPI:
	BASE_URL = "https://api.sleeper.app/v1"

	def __init__(self):
		self.cache_manager = CacheManager()
		self.league_manager = LeagueManager(self.BASE_URL, self.cache_manager)
		self.scoring_settings = self.league_manager.scoring_settings
		self.player_manager = PlayerManager()
		self.season_manager = SeasonManager()
		self.stats_manager = StatsManager(self, self.cache_manager, self.scoring_settings)
		self.matchup_manager = MatchupManager(self, self.cache_manager)
		self.projections_manager = ProjectionsManager(self.cache_manager)
		self.transaction_manager = TransactionManager(self)
		self.best_ball_manager = BestBallManager(self)
		self.standings_manager = StandingsManager(self)
		self.team_manager = TeamManager()
		self.draft_manager = DraftManager(self)
		
		# Pre-load historical transactions into cache
		if len(self.cache_manager.api_cache) == 0:  # Only load if cache is empty
			print("Loading historical transaction data...")
			current_league_id = "1048308938824937472"  # 2024 league
			self.transaction_manager.get_all_historical_transactions(current_league_id)

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
		if cache_key in self.cache_manager.api_cache:
			return self.cache_manager.api_cache[cache_key]

		response = requests.get(endpoint)
		if response.status_code == 200:
			data = response.json()
			self.cache_manager.api_cache[cache_key] = data
			self.cache_manager.save_api_cache()
			return data
		else:
			raise SleeperAPIException(f"API request failed: {response.status_code} - {response.text}")
