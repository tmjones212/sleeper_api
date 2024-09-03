from typing import List, Dict, Tuple
from models import League, Team, Matchup
from client import SleeperAPI

class LeagueAnalytics:
    def __init__(self, client: SleeperAPI):
        self.client = client
        self.valid_positions = ["QB", "RB", "WR", "TE"]

    def get_top_half_scorers(self, league_id: str, week: int) -> List[Dict[str, any]]:
        league = self.client.get_league(league_id, fetch_all=True)
        matchups = self.client.get_matchups(league_id, week)
        
        # Create a dictionary of team names keyed by roster_id
        team_dict = {team.roster.roster_id: team.display_name for team in league.teams if team.roster}
        
        # Collect all scores for the week
        scores = []
        for matchup in matchups:
            team_name = team_dict.get(matchup.roster_id, f"Team {matchup.roster_id}")
            scores.append({
                "team_name": team_name,
                "points": matchup.points,
                "roster_id": matchup.roster_id
            })
        
        # Sort scores from highest to lowest
        scores.sort(key=lambda x: x["points"], reverse=True)
        
        # Determine the number of teams in the top half
        top_half_count = len(scores) // 2
        if len(scores) % 2 != 0:
            top_half_count += 1  # If odd number of teams, include the middle team
        
        return scores[:top_half_count]

    def print_weekly_top_half_scorers(self, league_id: str):
        league = self.client.get_league(league_id)
        print("Week|Team|Points")
        for week in range(league.settings.start_week, league.settings.playoff_week_start):
            top_scorers = self.get_top_half_scorers(league_id, week)
            for scorer in top_scorers:
                print(f"{week}|{scorer['team_name']}|{scorer['points']:.2f}")

    def _calculate_best_ball_points(self, players_points: Dict[str, float], roster_positions: List[str]) -> Tuple[float, List[Dict[str, any]]]:
        valid_positions = ["QB", "RB", "WR", "TE"]
        position_players = {pos: [] for pos in valid_positions}
        
        for player_id, points in players_points.items():
            position = self.client.get_player_position(player_id)
            if position in valid_positions:
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
        
        for pos in roster_positions:
            if pos == "QB":
                add_to_lineup("QB")
            elif pos == "RB":
                add_to_lineup("RB")
            elif pos == "WR":
                add_to_lineup("WR")
            elif pos == "TE":
                add_to_lineup("TE")
            elif pos == "FLEX":
                flex_options = position_players["RB"] + position_players["WR"] + position_players["TE"]
                if flex_options:
                    best_flex = max(flex_options, key=lambda x: x["points"])
                    best_lineup.append({"position": "FLEX", "player": best_flex})
                    total_points += best_flex["points"]
                    position_players[best_flex["position"]].remove(best_flex)
            elif pos == "SUPER_FLEX":
                superflex_options = position_players["QB"] + position_players["RB"] + position_players["WR"] + position_players["TE"]
                if superflex_options:
                    best_superflex = max(superflex_options, key=lambda x: x["points"])
                    best_lineup.append({"position": "SUPER_FLEX", "player": best_superflex})
                    total_points += best_superflex["points"]
                    position_players[best_superflex["position"]].remove(best_superflex)
        
        return total_points, best_lineup

    def get_best_ball_scores(self, league_id: str, week: int) -> List[Dict[str, any]]:
        print(f"Getting best ball scores for week {week}... ")
        league = self.client.get_league(league_id, fetch_all=True)
        matchups = self.client.get_matchups(league_id, week)
        
        team_dict = {team.roster.roster_id: team for team in league.teams if team.roster}
        
        best_ball_scores = []
        for matchup in matchups:
            team = team_dict.get(matchup.roster_id)
            team_name = team.display_name if team else f"Team {matchup.roster_id}"
            print(f"Calculating best ball points for {team_name}... ")
            best_ball_points, best_lineup = self._calculate_best_ball_points(matchup.players_points, league.roster_positions)
            print(f"Best ball points for {team_name}: {best_ball_points}")
            best_ball_scores.append({
                "team_name": team_name,
                "actual_points": matchup.points,
                "best_ball_points": best_ball_points,
                "roster_id": matchup.roster_id,
                "best_lineup": best_lineup
            })
        
        return best_ball_scores

    def get_team_best_ball(self, league_id: str, team_name: str, week: int) -> Dict[str, any]:
        best_ball_scores = self.get_best_ball_scores(league_id, week)
        for score in best_ball_scores:
            if score["team_name"].lower() == team_name.lower():
                return score
        return None

    def print_team_best_ball(self, league_id: str, team_name: str, week: int):
        team_best_ball = self.get_team_best_ball(league_id, team_name, week)
        if team_best_ball:
            print(f"Best Ball for {team_best_ball['team_name']} in Week {week}:")
            print(f"Actual Points: {team_best_ball['actual_points']:.2f}")
            print(f"Best Ball Points: {team_best_ball['best_ball_points']:.2f}")
            print("\nBest Lineup:")
            for slot in team_best_ball['best_lineup']:
                player = slot['player']
                print(f"{slot['position']}: {self.client.get_player_name(player['id'])} - {player['points']:.2f}")
        else:
            print(f"No data found for team {team_name} in week {week}")

    def get_season_best_ball_total(self, league_id: str) -> Dict[str, List[Dict[str, any]]]:
        league = self.client.get_league(league_id, fetch_all=True)
        team_totals = {team.roster.roster_id: {
            'team_name': team.display_name,
            'total_best_ball_points': 0,
            'total_actual_points': 0,
            'weekly_scores': []
        } for team in league.teams if team.roster}

        start_week = league.settings.start_week
        end_week = league.settings.playoff_week_start

        for week in range(start_week, end_week):
            matchups = self.client.get_matchups(league_id, week)
            for matchup in matchups:
                best_ball_points, _ = self._calculate_best_ball_points(matchup.players_points, league.roster_positions)
                actual_points = self._calculate_actual_points(matchup.players_points, matchup.starters)
                team_data = team_totals[matchup.roster_id]
                team_data['total_best_ball_points'] += best_ball_points
                team_data['total_actual_points'] += actual_points
                team_data['weekly_scores'].append({
                    'week': week,
                    'best_ball_points': best_ball_points,
                    'actual_points': actual_points
                })

        return {'teams': sorted(team_totals.values(), key=lambda x: x['total_best_ball_points'], reverse=True)}

    def _calculate_actual_points(self, players_points: Dict[str, float], starters: List[str]) -> float:
        return sum(players_points[player] for player in starters if self.client.get_player_position(player) in self.valid_positions)

    def print_season_best_ball_total(self, league_id: str):
        season_total = self.get_season_best_ball_total(league_id)
        print("TeamName|TotalPointsScored|BestBallPointsScored|Difference")
        for team in season_total['teams']:
            diff = team['total_best_ball_points'] - team['total_actual_points']
            print(f"{team['team_name']}|{team['total_actual_points']:.2f}|{team['total_best_ball_points']:.2f}|{diff:.2f}")

    def get_weekly_best_ball_scores(self, league_id: str) -> Dict[str, List[Dict[str, any]]]:
        league = self.client.get_league(league_id, fetch_all=True)
        team_scores = {team.roster.roster_id: {
            'team_name': team.display_name,
            'weekly_scores': []
        } for team in league.teams if team.roster}

        start_week = league.settings.start_week
        end_week = league.settings.playoff_week_start

        for week in range(start_week, end_week):
            matchups = self.client.get_matchups(league_id, week)
            for matchup in matchups:
                best_ball_points, _ = self._calculate_best_ball_points(matchup.players_points, league.roster_positions)
                actual_points = self._calculate_actual_points(matchup.players_points, matchup.starters)
                team_data = team_scores[matchup.roster_id]
                team_data['weekly_scores'].append({
                    'week': week,
                    'actual_points': actual_points,
                    'best_ball_points': best_ball_points,
                    'difference': best_ball_points - actual_points
                })

        return team_scores

    def print_weekly_best_ball_scores(self, league_id: str, team_name: str = None):
        weekly_scores = self.get_weekly_best_ball_scores(league_id)
        
        print("TeamName|Week|TotalPointsScored|BestBallPointsScored|Difference")
        
        for team_id, team_data in weekly_scores.items():
            if team_name is None or team_data['team_name'].lower() == team_name.lower():
                for week_score in team_data['weekly_scores']:
                    print(f"{team_data['team_name']}|{week_score['week']}|{week_score['actual_points']:.2f}|{week_score['best_ball_points']:.2f}|{week_score['difference']:.2f}")

    # ... (other methods remain the same)