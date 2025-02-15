from typing import List
from models import PlayerProjection, SleeperProjections

class ProjectionsManager:
    def __init__(self, cache_manager):
        self.cache_manager = cache_manager

    def get_projections(self, year: int, week: int, position: str) -> List[PlayerProjection]:
        cache_key = f"{year}_{week}_{position}"
        if cache_key in self.cache_manager.projections_cache:
            return self.cache_manager.projections_cache[cache_key]

        projections = SleeperProjections.get_projections(year, week, position)
        self.cache_manager.projections_cache[cache_key] = projections
        self.cache_manager.save_projections_cache()
        return projections 