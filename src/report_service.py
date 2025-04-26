import csv
from player_extensions import format_name

class ReportService:
    def __init__(self, client):
        self.client = client

    def write_bench_players_stats_csv(self, league_id, csv_filename):
        client = self.client
        ktc = client.draft_service.get_ktc_player_value()
        positions = ["RB", "WR", "TE", "QB"]

        # Gather stats for all weeks and positions
        all_weekly_stats = {}
        for week in range(1, 19):
            all_weekly_stats[week] = {}
            for position in positions:
                position_stats = client.stats_service.get_stats(2024, week, position, league_id)
                all_weekly_stats[week].update(position_stats)

        # Map roster_id to team name
        rosters = client.league_service.get_league_rosters(league_id)
        users = client.league_service.get_league_users(league_id)
        roster_to_team = {}
        for roster in rosters:
            team = next((u for u in users if u.user_id == roster.owner_id), None)
            if team:
                roster_to_team[roster.roster_id] = team.display_name

        # Collect bench players by week
        bench_players_by_week = {}
        for week in range(1, 19):
            matchups = client.matchup_service.get_matchups(league_id, week)
            bench_players_by_week[week] = {}
            for matchup in matchups:
                team_name = roster_to_team.get(matchup.roster_id, f"Team {matchup.roster_id}")
                for player_id in matchup.players:
                    if player_id not in matchup.starters:
                        bench_players_by_week[week][player_id] = {
                            'stats': all_weekly_stats[week].get(player_id, None),
                            'team': team_name
                        }

        # Write to CSV
        with open(csv_filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Year', 'Week', 'Team', 'PlayerName', 'PlayerID', 'Position', 'Points', 'Status', 'SnapsPlayed', 'KTC'])
            for week in range(1, 19):
                for player_id, data in bench_players_by_week[week].items():
                    player_name = client.player_service.get_player_name(player_id)
                    player_position = client.player_service.get_player_position(player_id)
                    stats = data['stats']
                    if stats is None:
                        points = 0
                        active_status = "Did Not Play"
                        snaps = 0
                    else:
                        points = stats.fantasy_points
                        active_status = "Played" if stats.gp > 0 else "Did Not Play"
                        snaps = stats.off_snp
                    ktc_value = None
                    for ktc_player in ktc:
                        if ktc_player.get('name') and format_name(ktc_player['name']) == format_name(player_name):
                            ktc_value = ktc_player.get('value', 0)
                            break
                    writer.writerow([
                        2024, week, data['team'], player_name, player_id, player_position,
                        points, active_status, snaps, ktc_value
                    ])
        return csv_filename 