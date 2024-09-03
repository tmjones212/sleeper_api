from typing import List, Dict
from models import League, Team, Matchup
from client import SleeperAPI

class LeagueAnalytics:
    def __init__(self, client: SleeperAPI):
        self.client = client

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
