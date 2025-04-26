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
        url = f"https://api.sleeper.com/stats/nfl/{year}/{week}?season_type=regular&position={position.upper()}&order_by=pts_ppr"
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
            # Debug print to see problematic records
            print(f"\nDebug: Processing player data:")
            print(player_data)
            
            # Skip records without player_id or stats
            if 'player_id' not in player_data:
                print("Warning: Skipping record without player_id")
                continue
            
            if 'stats' not in player_data:
                print(f"Warning: Skipping player {player_data['player_id']} - no stats found")
                continue

            player_id = player_data['player_id']
            player_stats = player_data['stats']
            fantasy_points = self._calculate_fantasy_points(player_stats, scoring_settings)
            
            try:
                stats[player_id] = PlayerStats(
                    player_id=player_id,
                    fantasy_points=fantasy_points,
                    **player_stats
                )
                print(f"Debug: Successfully processed player {player_id} - Fantasy Points: {fantasy_points}")
            except Exception as e:
                print(f"Error processing player {player_id}: {str(e)}")
                continue

        self.cache_service.stats_cache[cache_key] = stats
        self.cache_service.save_stats_cache()
        return stats

    def _calculate_fantasy_points(self, player_stats: Dict[str, float], scoring_settings: Dict[str, float]) -> float:
        fantasy_points = 0
        for stat, value in player_stats.items():
            if stat in scoring_settings:
                fantasy_points += value * scoring_settings[stat]
        return round(fantasy_points , 2)