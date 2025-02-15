from typing import List, Dict, Any, Tuple
import os
import csv
from datetime import datetime

class BestBallService:
    def __init__(self, client):
        self.client = client
        self.valid_positions = ["QB", "RB", "WR", "TE", "K", "DB", "LB", "DE", "DL", "DT", "CB", "S"]
        self.defensive_positions = ["DB", "LB", "DE", "DL", "DT", "CB", "S"]
        self.offensive_positions = ["QB", "RB", "WR", "TE", "FLEX", "SUPER_FLEX"]

    def _calculate_best_ball_points(self, players_points: Dict[str, float], roster_positions: List[str]) -> Tuple[float, List[Dict[str, any]]]:
        position_players = {pos: [] for pos in self.valid_positions + ["FLEX", "SUPER_FLEX", "IDP_FLEX"]}
        
        for player_id, points in players_points.items():
            position = self.client.player_service.get_player_position(player_id)
            if position in self.valid_positions:
                position_players[position].append({"id": player_id, "points": points, "position": position})
        
        for pos in position_players:
            position_players[pos].sort(key=lambda x: x["points"], reverse=True)
        
        best_lineup = []
        total_points = 0
        
        def add_to_lineup(pos):
            nonlocal total_points
            if position_players[pos]:
                player = position_players[pos].pop(0)
                best_lineup.append({"position": pos, "player": player})
                total_points += player["points"]
                return True
            return False
        
        # Fill standard positions first
        for pos in roster_positions:
            if pos in self.valid_positions:
                add_to_lineup(pos)
        
        # Handle FLEX spots
        flex_positions = ["RB", "WR", "TE"]
        for pos in roster_positions:
            if pos == "FLEX":
                flex_options = [player for pos in flex_positions for player in position_players[pos]]
                if flex_options:
                    best_flex = max(flex_options, key=lambda x: x["points"])
                    best_lineup.append({"position": "FLEX", "player": best_flex})
                    total_points += best_flex["points"]
                    position_players[best_flex["position"]].remove(best_flex)
        
        # Handle SUPER_FLEX spots
        superflex_positions = ["QB", "RB", "WR", "TE"]
        for pos in roster_positions:
            if pos == "SUPER_FLEX":
                superflex_options = [player for pos in superflex_positions for player in position_players[pos]]
                if superflex_options:
                    best_superflex = max(superflex_options, key=lambda x: x["points"])
                    best_lineup.append({"position": "SUPER_FLEX", "player": best_superflex})
                    total_points += best_superflex["points"]
                    position_players[best_superflex["position"]].remove(best_superflex)

        # Handle IDP_FLEX spots
        for pos in roster_positions:
            if pos == "IDP_FLEX":
                idp_options = [player for pos in self.defensive_positions for player in position_players[pos]]
                if idp_options:
                    best_idp = max(idp_options, key=lambda x: x["points"])
                    best_lineup.append({"position": "IDP_FLEX", "player": best_idp})
                    total_points += best_idp["points"]
                    position_players[best_idp["position"]].remove(best_idp)

        return total_points, best_lineup

    def get_best_ball_scores(self, league_id: str, week: int) -> List[Dict[str, any]]:
        league = self.client.league_service.get_league(league_id, fetch_all=True)
        matchups = self.client.matchup_service.get_matchups(league_id, week)
        
        team_dict = {team.roster.roster_id: team for team in league.teams if team.roster}
        
        best_ball_scores = []
        for matchup in matchups:
            team = team_dict.get(matchup.roster_id)
            team_name = team.display_name if team else f"Team {matchup.roster_id}"
            
            # Calculate actual points
            actual_points = sum(matchup.starters_points)
            
            # Calculate best ball points
            best_ball_points, best_lineup = self._calculate_best_ball_points(
                matchup.players_points, 
                league.roster_positions
            )
            
            best_ball_scores.append({
                "week": week,
                "team_name": team_name,
                "actual_points": actual_points,
                "best_ball_points": best_ball_points,
                "roster_id": matchup.roster_id,
                "best_lineup": best_lineup
            })
        
        return best_ball_scores

    def get_season_best_ball_total(self, league_id: str) -> Dict[str, List[Dict[str, any]]]:
        league = self.client.league_service.get_league(league_id, fetch_all=True)
        team_totals = {team.roster.roster_id: {
            'team_name': team.display_name,
            'total_best_ball_points': 0,
            'total_actual_points': 0,
            'total_offensive_best_ball_points': 0,
            'wins': 0,
            'half_wins': 0,
            'weekly_scores': []
        } for team in league.teams if team.roster}

        start_week = league.settings.start_week
        end_week = league.settings.playoff_week_start

        for week in range(start_week, end_week):
            matchups = self.client.matchup_service.get_matchups(league_id, week)
            
            # Calculate half wins for the week
            week_scores = [(matchup.roster_id, sum(matchup.starters_points)) for matchup in matchups]
            week_scores.sort(key=lambda x: x[1], reverse=True)
            half_win_threshold = len(week_scores) // 2
            
            for idx, (roster_id, score) in enumerate(week_scores):
                if idx < half_win_threshold:
                    team_totals[roster_id]['half_wins'] += 0.5

            for matchup in matchups:
                best_ball_points, best_lineup = self._calculate_best_ball_points(
                    matchup.players_points, 
                    league.roster_positions
                )
                actual_points = sum(matchup.starters_points)
                offensive_best_ball_points = self._calculate_offensive_best_ball_points(best_lineup)
                
                team_data = team_totals[matchup.roster_id]
                team_data['total_best_ball_points'] += best_ball_points
                team_data['total_actual_points'] += actual_points
                team_data['total_offensive_best_ball_points'] += offensive_best_ball_points
                team_data['weekly_scores'].append({
                    'week': week,
                    'best_ball_points': best_ball_points,
                    'actual_points': actual_points,     
                    'offensive_best_ball_points': offensive_best_ball_points
                })
                
                # Calculate head-to-head win
                opponent = next((m for m in matchups if m.matchup_id == matchup.matchup_id and m.roster_id != matchup.roster_id), None)
                if opponent and actual_points > sum(opponent.starters_points):
                    team_data['wins'] += 1

        return {'teams': sorted(team_totals.values(), key=lambda x: x['total_best_ball_points'], reverse=True)}

    def _calculate_offensive_best_ball_points(self, best_lineup: List[Dict[str, Any]]) -> float:
        return sum(slot['player']['points'] for slot in best_lineup 
                  if slot['position'] in self.offensive_positions)

    def write_offensive_best_ball_to_csv(self, league_id: str, filename: str = "data/offensive_best_ball.csv"):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        league = self.client.league_service.get_league(league_id, fetch_all=True)
        current_week = self.client.season_service.get_current_week()
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Week', 'TeamName', 'PlayerName', 'LineupPosition', 'Points'])
            
            for week in range(league.settings.start_week, current_week):
                best_ball_scores = self.get_best_ball_scores(league_id, week)
                
                for score in best_ball_scores:
                    team_name = score['team_name']
                    # Filter for offensive positions only
                    offensive_lineup = [
                        slot for slot in score['best_lineup'] 
                        if slot['position'] in self.offensive_positions
                    ]
                    
                    for slot in offensive_lineup:
                        player_id = slot['player']['id']
                        player_name = self.client.player_service.get_player_name(player_id)
                        writer.writerow([
                            week,
                            team_name,
                            player_name,
                            slot['position'],
                            f"{slot['player']['points']:.2f}"
                        ]) 