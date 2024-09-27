from typing import List, Dict, Tuple, Any
from exceptions import SleeperAPIException
from models import League, Team, Matchup, PlayerStats
from client import SleeperAPI
from datetime import datetime

class LeagueAnalytics:
    def __init__(self, client: SleeperAPI):
        self.client = client
        self.valid_positions = ["QB", "RB", "WR", "TE","K","DB","LB","DE","DL","DT","CB","S"]
        self.defensive_positions = ["DB", "LB", "DE", "DL", "DT", "CB", "S"]
        self.stats_cache = {}
        self.current_year = self.client.get_current_season_year()
        self.current_week = self.client.get_current_week()
        self.league_id = None  # Initialize league_id as None
        self.traded_picks = {}

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
        print("Debug: Entering _calculate_best_ball_points method")
        for player_id, points in players_points.items():
            player_name = self.client.get_player_name(player_id)
            player_position = self.client.get_player_position(player_id)
            print(f"Player: {player_name} ({player_position}) - ID: {player_id}, Points: {points}")
        print("---")

        position_players = {pos: [] for pos in self.valid_positions + ["FLEX", "SUPER_FLEX", "IDP_FLEX"]}
        
        for player_id, points in players_points.items():
            position = self.client.get_player_position(player_id)
            if position in self.valid_positions:
                position_players[position].append({"id": player_id, "points": points, "position": position})
        
        for pos in position_players:
            position_players[pos].sort(key=lambda x: x["points"], reverse=True)
            print(f"Debug: Sorted {pos} players: {position_players[pos]}")
        
        best_lineup = []
        total_points = 0
        
        def add_to_lineup(pos):
            nonlocal total_points
            if position_players[pos]:
                player = position_players[pos].pop(0)
                best_lineup.append({"position": pos, "player": player})
                total_points += player["points"]
                player_name = self.client.get_player_name(player['id'])
                print(f"Debug: Added {pos}: {player_name} (ID: {player['id']}) with {player['points']} points")
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
                    player_name = self.client.get_player_name(best_flex['id'])
                    print(f"Debug: Added FLEX: {player_name} (ID: {best_flex['id']}) with {best_flex['points']} points")
        
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
                    player_name = self.client.get_player_name(best_superflex['id'])
                    print(f"Debug: Added SUPER_FLEX: {player_name} (ID: {best_superflex['id']}) with {best_superflex['points']} points")

        # Handle IDP_FLEX spots
        for pos in roster_positions:
            if pos == "IDP_FLEX":
                idp_options = [player for pos in self.defensive_positions for player in position_players[pos]]
                if idp_options:
                    best_idp = max(idp_options, key=lambda x: x["points"])
                    best_lineup.append({"position": "IDP_FLEX", "player": best_idp})
                    total_points += best_idp["points"]
                    position_players[best_idp["position"]].remove(best_idp)
                    player_name = self.client.get_player_name(best_idp['id'])
                    print(f"Debug: Added IDP_FLEX: {player_name} (ID: {best_idp['id']}) with {best_idp['points']} points")
        
        print(f"Debug: Total Best Ball Points: {total_points}")
        print("Debug: Best Lineup:")
        for slot in best_lineup:
            player = slot['player']
            player_name = self.client.get_player_name(player['id'])
            print(f"{slot['position']}: {player_name} - {player['points']:.2f}")
        print("---")

        return total_points, best_lineup

    def get_best_ball_scores(self, league_id: str, week: int) -> List[Dict[str, any]]:
        league = self.client.get_league(league_id, fetch_all=True)
        matchups = self.client.get_matchups(league_id, week)
        
        self.current_year = int(league.season)
        self.current_week = week
        self.league_id = league_id
        
        team_dict = {team.roster.roster_id: team for team in league.teams if team.roster}
        
        best_ball_scores = []
        for matchup in matchups:
            team = team_dict.get(matchup.roster_id)
            team_name = team.display_name if team else f"Team {matchup.roster_id}"
            
            # Calculate actual points
            actual_points = sum(matchup.starters_points)
            
            # Calculate best ball points
            best_ball_points, best_lineup = self._calculate_best_ball_points(matchup.players_points, league.roster_positions)
            
            best_ball_scores.append({
                "week": week,
                "team_name": team_name,
                "actual_points": actual_points,
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

    def print_season_best_ball_total(self, league_id: str):
        totals = self.get_season_best_ball_total(league_id)
        print("Team|Total Best Ball|Total Actual|Total Offensive Best Ball|Wins|Half Wins|Original Draft Team|Current Owner")
        for team in totals['teams']:
            original_draft_team = team['weekly_scores'][0]['original_draft_team'] if team['weekly_scores'] else "Unknown"
            current_owner = team['weekly_scores'][0]['current_owner'] if team['weekly_scores'] else "Unknown"
            print(f"{team['team_name']}|{team['total_best_ball_points']:.2f}|{team['total_actual_points']:.2f}|{team['total_offensive_best_ball_points']:.2f}|{team['wins']}|{team['half_wins']:.1f}|{original_draft_team}|{current_owner}")

    def get_season_best_ball_total(self, league_id: str) -> Dict[str, List[Dict[str, any]]]:
        self.league_id = league_id  # Set the league_id
        league = self.client.get_league(league_id, fetch_all=True)
        team_totals = {team.roster.roster_id: {
            'team_name': team.display_name,
            'total_best_ball_points': 0,
            'total_actual_points': 0,
            'total_offensive_best_ball_points': 0,
            'wins': 0,
            'half_wins': 0,
            'weekly_scores': []
        } for team in league.teams if team.roster}

        current_week = self.client.get_current_week()
        start_week = league.settings.start_week

        for week in range(start_week, current_week):
            print(f"\nWeek {week}")
            matchups = self.client.get_matchups(league_id, week)
            
            # Calculate half wins for the week
            week_scores = [(matchup.roster_id, sum(matchup.starters_points)) for matchup in matchups]
            week_scores.sort(key=lambda x: x[1], reverse=True)
            half_win_threshold = len(week_scores) // 2
            
            for idx, (roster_id, score) in enumerate(week_scores):
                if idx < half_win_threshold:
                    team_totals[roster_id]['half_wins'] += 0.5

            for matchup in matchups:
                print(f"\nTeam: {team_totals[matchup.roster_id]['team_name']}")
                for player_id, points in matchup.players_points.items():
                    player_name = self.client.get_player_name(player_id)
                    player_position = self.client.get_player_position(player_id)
                    print(f"Player: {player_name} ({player_position}) - ID: {player_id}, Points: {points}")
                print("---")
                
                best_ball_points, best_lineup = self._calculate_best_ball_points(matchup.players_points, league.roster_positions)
                actual_points = self._calculate_actual_points(matchup.players_points, matchup.starters)
                offensive_best_ball_points = self._calculate_offensive_best_ball_points(best_lineup)
                team_data = team_totals[matchup.roster_id]
                team_data['total_best_ball_points'] += best_ball_points
                team_data['total_actual_points'] += actual_points
                team_data['total_offensive_best_ball_points'] += offensive_best_ball_points
                
                # Add draft pick information
                current_year = self.client.get_current_season_year()
                original_owner_id = self.get_original_draft_team(league_id, matchup.roster_id, 1, str(current_year))
                original_owner = next((team for team in league.teams if team.roster and team.roster.roster_id == original_owner_id), None)
                original_owner_name = original_owner.display_name if original_owner else f"Unknown (ID: {original_owner_id})"
                current_owner = next((team for team in league.teams if team.roster and team.roster.roster_id == matchup.roster_id), None)
                current_owner_name = current_owner.display_name if current_owner else f"Unknown (ID: {matchup.roster_id})"

                team_data['weekly_scores'].append({
                    'week': week,
                    'best_ball_points': best_ball_points,
                    'actual_points': actual_points,     
                    'offensive_best_ball_points': offensive_best_ball_points,
                    'original_draft_team': original_owner_name,
                    'current_owner': current_owner_name
                })
                
                # Calculate head-to-head win
                opponent = next((m for m in matchups if m.matchup_id == matchup.matchup_id and m.roster_id != matchup.roster_id), None)
                if opponent and actual_points > sum(opponent.starters_points):
                    team_data['wins'] += 1
                
                print(f"Weekly Best Ball Points: {best_ball_points:.2f}")
                print(f"Weekly Actual Points: {actual_points:.2f}")
                print(f"Weekly Offensive Best Ball Points: {offensive_best_ball_points:.2f}")
                print(f"Cumulative Best Ball Points: {team_data['total_best_ball_points']:.2f}")
                print(f"Cumulative Actual Points: {team_data['total_actual_points']:.2f}")
                print(f"Cumulative Offensive Best Ball Points: {team_data['total_offensive_best_ball_points']:.2f}")
                print(f"Wins: {team_data['wins']}, Half Wins: {team_data['half_wins']:.1f}")
                print("Best Ball Lineup:")
                for slot in best_lineup:
                    player = slot['player']
                    player_name = self.client.get_player_name(player['id'])
                    print(f"{slot['position']}: {player_name} - {player['points']:.2f}")

        return {'teams': sorted(team_totals.values(), key=lambda x: x['total_best_ball_points'], reverse=True)}

    def _calculate_actual_points(self, players_points: Dict[str, float], starters: List[str]) -> float:
        return sum(players_points[player] for player in starters if self.client.get_player_position(player) in self.valid_positions)

    def _calculate_offensive_best_ball_points(self, best_lineup: List[Dict[str, Any]]) -> float:
        offensive_positions = ["QB", "RB", "WR", "TE", "FLEX", "SUPER_FLEX"]
        return sum(slot['player']['points'] for slot in best_lineup if slot['position'] in offensive_positions)

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
        league = self.client.get_league(league_id, fetch_all=True)
        start_week = league.settings.start_week
        end_week = league.settings.playoff_week_start

        # Initialize win counters
        win_counts = {team.roster.roster_id: {'wins': 0, 'half_wins': 0} for team in league.teams if team.roster}
        
        all_scores = []

        for week in range(start_week, end_week):
            week_scores = self.get_best_ball_scores(league_id, week)
            
            # Calculate wins and half-wins
            sorted_scores = sorted(week_scores, key=lambda x: x['actual_points'], reverse=True)
            half_win_threshold = len(sorted_scores) // 2
            
            for i, score in enumerate(sorted_scores):
                if i < half_win_threshold:
                    win_counts[score['roster_id']]['half_wins'] += 0.5
            
            # Pair up teams and determine head-to-head winners
            for i in range(0, len(sorted_scores), 2):
                if i + 1 < len(sorted_scores):
                    if sorted_scores[i]['actual_points'] > sorted_scores[i+1]['actual_points']:
                        win_counts[sorted_scores[i]['roster_id']]['wins'] += 1
                    elif sorted_scores[i]['actual_points'] < sorted_scores[i+1]['actual_points']:
                        win_counts[sorted_scores[i+1]['roster_id']]['wins'] += 1
            
            all_scores.extend(week_scores)

        # Sort all scores by week and then by best ball points
        all_scores.sort(key=lambda x: (x['week'], -x['best_ball_points']))

        print("Week|TeamName|ActualPoints|BestBallPoints|Difference|Wins|HalfWins")
        for score in all_scores:
            if team_name is None or score['team_name'].lower() == team_name.lower():
                wins = win_counts[score['roster_id']]['wins']
                half_wins = win_counts[score['roster_id']]['half_wins']
                difference = score['best_ball_points'] - score['actual_points']
                print(f"{score['week']}|{score['team_name']}|{score['actual_points']:.2f}|{score['best_ball_points']:.2f}|{difference:.2f}|{wins}|{half_wins:.1f}")

    def is_offensive_position(self, position: str) -> bool:
        offensive_positions = {"QB", "RB", "WR", "TE"}
        return position in offensive_positions

    def get_league_standings(self, league_id: str) -> List[Dict[str, Any]]:
        league = self.client.get_league(league_id, fetch_all=True)
        current_week = self.client.get_current_week()
        
        standings = {team.roster.roster_id: {
            'team_name': team.display_name,
            'wins': 0,
            'losses': 0,
            'ties': 0,
            'half_wins': 0,
            'points_for': 0,
            'points_against': 0,
            'best_ball_points': 0,
            'offensive_best_ball_points': 0
        } for team in league.teams if team.roster}

        for week in range(1, current_week):
            try:
                matchups = self.client.get_matchups(league_id, week)
                if not matchups:
                    print(f"Warning: No matchups found for week {week}")
                    continue

                best_ball_scores = self.get_best_ball_scores(league_id, week)
                
                # Sort teams by best ball points for this week
                sorted_scores = sorted(best_ball_scores, key=lambda x: x['best_ball_points'], reverse=True)
                half_win_threshold = len(sorted_scores) // 2

                for idx, score in enumerate(sorted_scores):
                    team = standings[score['roster_id']]
                    team['best_ball_points'] += score['best_ball_points']
                    team['offensive_best_ball_points'] += sum(
                        player['player']['points'] for player in score['best_lineup']
                        if self.is_offensive_position(player['position'])
                    )
                    
                    # Assign half win to top half of teams
                    if idx < half_win_threshold:
                        team['half_wins'] += 0.5

                for matchup in matchups:
                    team = standings[matchup.roster_id]
                    team['points_for'] += matchup.points
                    
                    # Find the opponent
                    opponent = next((m for m in matchups if m.matchup_id == matchup.matchup_id and m.roster_id != matchup.roster_id), None)
                    if opponent:
                        team['points_against'] += opponent.points
                        
                        if matchup.points > opponent.points:
                            team['wins'] += 1
                        elif matchup.points < opponent.points:
                            team['losses'] += 1
                        else:
                            team['ties'] += 1

            except SleeperAPIException as e:
                print(f"Error fetching data for week {week}: {str(e)}. Skipping...")
                continue

        sorted_standings = sorted(
            standings.values(),
            key=lambda x: (x['wins'] + x['half_wins'], x['points_for']),
            reverse=True
        )

        return sorted_standings

    def print_league_standings(self, league_id: str):
        standings = self.get_league_standings(league_id)
        print("Rank|Team|W-L-T|Half Wins|PF|PA|BB Points|Off BB Points")
        for rank, team in enumerate(standings, 1):
            print(f"{rank}|{team['team_name']}|{team['wins']}-{team['losses']}-{team['ties']}|{team['half_wins']:.1f}|{team['points_for']:.2f}|{team['points_against']:.2f}|{team['best_ball_points']:.2f}|{team['offensive_best_ball_points']:.2f}")

    def get_player_stats(self, year: int, week: int, position: str, league_id: str) -> Dict[str, PlayerStats]:
        return self.client.get_stats(year, week, position, league_id)

    def get_original_draft_team(self, league_id: str, current_owner_id: int, round: int, season: str) -> int:
        if not self.traded_picks:
            self.traded_picks = self.client.get_all_traded_picks(league_id)

        for pick in self.traded_picks:
            if (pick['owner_id'] == current_owner_id and
                pick['round'] == round and
                pick['season'] == season):
                return pick['roster_id']  # This is the original owner

        return current_owner_id  # If no trade found, assume it's the original owner