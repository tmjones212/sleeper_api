import json
from json import JSONEncoder

from models import PlayerInfo, PlayerProjection, PlayerStats, ProjectedStats

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, PlayerProjection):
            return {
                'player': self.default(obj.player),
                'stats': self.default(obj.stats),
                'week': obj.week,
                'year': obj.year,
                'opponent': obj.opponent
            }
        elif isinstance(obj, PlayerInfo):
            return {
                'player_id': obj.player_id,
                'first_name': obj.first_name,
                'last_name': obj.last_name,
                'position': obj.position,
                'team': obj.team,
                'injury_status': obj.injury_status
            }
        elif isinstance(obj, ProjectedStats):
            return obj.__dict__
        elif isinstance(obj, PlayerStats):
            return obj.__dict__
        return super().default(obj)