from typing import Dict, Any
import requests
from models import PlayerStats

class StatsService:
    def __init__(self, base_url: str, cache_service, scoring_settings: Dict[str, Dict[str, float]]):
        self.base_url = base_url
        self.cache_service = cache_service
        self.scoring_settings = scoring_settings

    def get_stats(self, year: int, week: int, position: str, league_id: str) -> Dict[str, PlayerStats]:
        cache_key = f"{year}_{week}_{position}_{league_id}"
        if cache_key in self.cache_service.stats_cache:
            print(f"Debug: Using cached stats for {cache_key}")
            return self.cache_service.stats_cache[cache_key]

        print(f"Debug: Fetching stats for {cache_key}")
        url = f"{self.base_url}/stats/nfl/{year}/{week}?season_type=regular&position[]={position}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        print("Debug: Raw API response:")
        print(data)

        stats = {}
        scoring_settings = self.scoring_settings.get(league_id, {})

        # Handle the data whether it's a list or dictionary
        if isinstance(data, list):
            player_data_list = data
        else:
            player_data_list = [data]

        for player_data in player_data_list:
            player_id = player_data['player_id']
            player_stats = player_data['stats']
            fantasy_points = self._calculate_fantasy_points(player_stats, scoring_settings)
            stats[player_id] = PlayerStats(
                player_id=player_id,
                fantasy_points=fantasy_points,
                **player_stats
            )
            print(f"Debug: Player {player_id} - Fantasy Points: {fantasy_points}")

        self.cache_service.stats_cache[cache_key] = stats
        self.cache_service.save_stats_cache()
        return stats

    def _calculate_fantasy_points(self, player_stats: Dict[str, float], scoring_settings: Dict[str, float]) -> float:
        fantasy_points = 0
        for stat, value in player_stats.items():
            if stat in scoring_settings:
                fantasy_points += value * scoring_settings[stat]
        return fantasy_points 