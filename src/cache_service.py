import os
import json
from typing import Dict, Any
from models import PlayerInfo, PlayerStats, PlayerProjection, Matchup, Player, ProjectedStats
from customer_json_encoder import CustomJSONEncoder

class CacheService:
    def __init__(self):
        self.api_cache = self._load_api_cache()
        self.stats_cache = self._load_stats_cache()
        self.projections_cache = self._load_projections_cache()
        self.matchups_cache = self._load_matchups_cache()

    def _load_api_cache(self, filename="data/api_cache.json") -> Dict:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        return {}

    def _load_stats_cache(self, filename="data/stats_cache.json") -> Dict:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
                return {k: {player_id: PlayerStats(**stats) for player_id, stats in v.items()} 
                        for k, v in data.items()}
        return {}

    def _load_projections_cache(self, filename="data/projections_cache.json") -> Dict:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
                return {k: [self._reconstruct_player_projection(p) for p in v] 
                        for k, v in data.items()}
        return {}

    def _load_matchups_cache(self, filename="data/matchups_cache.json") -> Dict:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                serialized_cache = json.load(f)
                return {key: [Matchup(**matchup_data) for matchup_data in matchups]
                        for key, matchups in serialized_cache.items()}
        return {}

    def save_api_cache(self, filename="data/api_cache.json"):
        self._ensure_data_dir()
        with open(filename, 'w') as f:
            json.dump(self.api_cache, f, default=lambda o: vars(o) if hasattr(o, '__dict__') else str(o))

    def save_stats_cache(self, filename="data/stats_cache.json"):
        self._ensure_data_dir()
        with open(filename, 'w') as f:
            json.dump(self.stats_cache, f, cls=CustomJSONEncoder)

    def save_projections_cache(self, filename="data/projections_cache.json"):
        self._ensure_data_dir()
        with open(filename, 'w') as f:
            json.dump(self.projections_cache, f, cls=CustomJSONEncoder)

    def save_matchups_cache(self, filename="data/matchups_cache.json"):
        self._ensure_data_dir()
        serializable_cache = {
            key: [matchup.__dict__ for matchup in matchups]
            for key, matchups in self.matchups_cache.items()
        }
        with open(filename, 'w') as f:
            json.dump(serializable_cache, f)

    def clear_all_caches(self):
        self.api_cache = {}
        self.stats_cache = {}
        self.projections_cache = {}
        self.matchups_cache = {}
        self.save_api_cache()
        self.save_stats_cache()
        self.save_projections_cache()
        self.save_matchups_cache()

    @staticmethod
    def _ensure_data_dir():
        os.makedirs("data", exist_ok=True)

    @staticmethod
    def _reconstruct_player_projection(data):
        return PlayerProjection(
            player=PlayerInfo(**data['player']),
            stats=ProjectedStats(**data['stats']),
            week=data['week'],
            year=data['year'],
            opponent=data['opponent']
        ) 