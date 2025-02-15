from typing import List
from models import PlayerProjection, SleeperProjections

class ProjectionsService:
    def __init__(self, cache_service):
        self.cache_service = cache_service

    def get_projections(self, year: int, week: int, position: str) -> List[PlayerProjection]:
        cache_key = f"{year}_{week}_{position}"
        if cache_key in self.cache_service.projections_cache:
            return self.cache_service.projections_cache[cache_key]

        projections = SleeperProjections.get_projections(year, week, position)
        self.cache_service.projections_cache[cache_key] = projections
        self.cache_service.save_projections_cache()
        return projections 