from typing import Dict, List, Optional
import requests
from models import Matchup
from player_service import PlayerService

class MatchupService:
    def __init__(self, base_url: str, cache_service):
        self.base_url = base_url
        self.cache_service = cache_service

    def get_matchups(
        self,
        league_id: str,
        week: int,
        current_week: Optional[int] = None,
        players: Optional[list] = None
    ) -> List[dict]:
        cache_key = f"{league_id}_{week}"
        current_week = current_week or week

        players_dict = PlayerService.players_list_to_dict(players) if players and isinstance(players, list) else players

        if cache_key in self.cache_service.matchups_cache:
            cached_matchups = self.cache_service.matchups_cache[cache_key]
            if not (week < current_week and any(matchup.points == 0 for matchup in cached_matchups)):
                if players:
                    for matchup in cached_matchups:
                        if isinstance(matchup, dict):
                            player_ids = matchup.get('players', [])
                        else:
                            player_ids = getattr(matchup, 'players', [])
                        player_names = [
                            players_dict.get(pid).name if players_dict.get(pid) else '' for pid in player_ids
                        ]
                        if isinstance(matchup, dict):
                            matchup['player_names'] = player_names
                        else:
                            setattr(matchup, 'player_names', player_names)
                return cached_matchups

        url = f"{self.base_url}/league/{league_id}/matchups/{week}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        matchups = []
        for matchup_data in data:
            players_points = {}
            starters_points = []
            for player_id, points in matchup_data.get('players_points', {}).items():
                players_points[player_id] = points
                if player_id in matchup_data.get('starters', []):
                    starters_points.append(points)

            player_names = []
            if players:
                player_names = [
                    players_dict.get(pid).name if players_dict.get(pid) else '' for pid in matchup_data.get('players', [])
                ]

            matchup = Matchup(
                matchup_id=matchup_data.get('matchup_id'),
                roster_id=matchup_data.get('roster_id'),
                points=matchup_data.get('points'),
                players=matchup_data.get('players', []),
                starters=matchup_data.get('starters', []),
                players_points=players_points,
                starters_points=starters_points,
                custom_points=None
            )
            if player_names:
                setattr(matchup, 'player_names', player_names)
            matchups.append(matchup)

        self.cache_service.matchups_cache[cache_key] = matchups
        self.cache_service.save_matchups_cache()
        return matchups

    def get_all_matchups(self, league_id: str, current_week: int) -> Dict[int, List[Matchup]]:
        return {
            week: self.get_matchups(league_id, week, current_week)
            for week in range(1, current_week + 1)
        } 