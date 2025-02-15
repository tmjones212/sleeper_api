from typing import List, Dict, Any

class StandingsManager:
    def __init__(self, client):
        self.client = client

    def get_league_standings(self, league_id: str) -> List[Dict[str, Any]]:
        """Get current standings for a league including wins, losses, points for/against."""
        league = self.client.league_manager.get_league(league_id, fetch_all=True)
        current_week = self.client.season_manager.get_current_week()
        
        # Initialize standings dictionary
        standings = {team.roster.roster_id: {
            'team_name': team.display_name,
            'wins': 0,
            'losses': 0,
            'ties': 0,
            'points_for': 0,
            'points_against': 0,
            'half_wins': 0,
            'best_ball_points': 0,
            'offensive_best_ball_points': 0
        } for team in league.teams if team.roster}

        # Calculate standings for each week
        for week in range(league.settings.start_week, current_week):
            matchups = self.client.matchup_manager.get_matchups(league_id, week)
            if not matchups:
                break

            # Calculate points and record for each matchup
            for matchup in matchups:
                roster_id = matchup.roster_id
                points = sum(matchup.starters_points)
                standings[roster_id]['points_for'] += points

                # Calculate best ball points
                best_ball_points, best_lineup = self.client.best_ball_manager._calculate_best_ball_points(
                    matchup.players_points,
                    league.roster_positions
                )
                standings[roster_id]['best_ball_points'] += best_ball_points
                
                # Calculate offensive best ball points
                offensive_best_ball_points = self.client.best_ball_manager._calculate_offensive_best_ball_points(best_lineup)
                standings[roster_id]['offensive_best_ball_points'] += offensive_best_ball_points

                # Find opponent in same matchup
                opponent = next((m for m in matchups 
                               if m.matchup_id == matchup.matchup_id 
                               and m.roster_id != roster_id), None)
                
                if opponent:
                    opponent_points = sum(opponent.starters_points)
                    standings[roster_id]['points_against'] += opponent_points

                    if points > opponent_points:
                        standings[roster_id]['wins'] += 1
                    elif points < opponent_points:
                        standings[roster_id]['losses'] += 1
                    else:
                        standings[roster_id]['ties'] += 1

            # Calculate half wins for the week
            week_scores = [(m.roster_id, sum(m.starters_points)) for m in matchups]
            week_scores.sort(key=lambda x: x[1], reverse=True)
            half_win_threshold = len(week_scores) // 2
            
            for idx, (roster_id, _) in enumerate(week_scores):
                if idx < half_win_threshold:
                    standings[roster_id]['half_wins'] += 0.5

        # Sort standings by wins + half wins, then points for
        sorted_standings = sorted(
            standings.values(),
            key=lambda x: (x['wins'] + x['half_wins'], x['points_for']),
            reverse=True
        )

        return sorted_standings

    def get_top_half_scorers(self, league_id: str, week: int) -> List[Dict[str, any]]:
        """Get the top half scoring teams for a given week."""
        league = self.client.league_manager.get_league(league_id, fetch_all=True)
        matchups = self.client.matchup_manager.get_matchups(league_id, week)
        
        # Create a dictionary of team names keyed by roster_id
        team_dict = {team.roster.roster_id: team.display_name 
                    for team in league.teams if team.roster}
        
        # Collect all scores for the week
        scores = []
        for matchup in matchups:
            team_name = team_dict.get(matchup.roster_id, f"Team {matchup.roster_id}")
            scores.append({
                "team_name": team_name,
                "points": sum(matchup.starters_points),
                "roster_id": matchup.roster_id
            })
        
        # Sort scores from highest to lowest
        scores.sort(key=lambda x: x["points"], reverse=True)
        
        # Determine the number of teams in the top half
        top_half_count = len(scores) // 2
        if len(scores) % 2 != 0:
            top_half_count += 1  # If odd number of teams, include the middle team
        
        return scores[:top_half_count]

    def print_league_standings(self, league_id: str):
        """Print formatted league standings."""
        standings = self.get_league_standings(league_id)
        print("Rank|Team|W-L-T|Half Wins|PF|PA|BB Points|Off BB Points")
        for rank, team in enumerate(standings, 1):
            print(f"{rank}|{team['team_name']}|"
                  f"{team['wins']}-{team['losses']}-{team['ties']}|"
                  f"{team['half_wins']:.1f}|"
                  f"{team['points_for']:.2f}|"
                  f"{team['points_against']:.2f}|"
                  f"{team['best_ball_points']:.2f}|"
                  f"{team['offensive_best_ball_points']:.2f}")

    def print_weekly_top_half_scorers(self, league_id: str):
        """Print top half scorers for each week."""
        league = self.client.league_manager.get_league(league_id)
        print("Week|Team|Points")
        for week in range(league.settings.start_week, league.settings.playoff_week_start):
            top_scorers = self.get_top_half_scorers(league_id, week)
            for scorer in top_scorers:
                print(f"{week}|{scorer['team_name']}|{scorer['points']:.2f}") 