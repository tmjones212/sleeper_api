from client import SleeperAPI
from league_analytics import LeagueAnalytics

# league_id = "1048308938824937472" # 2024
league_id = "916445745966915584" # 2023

client = SleeperAPI()
analytics = LeagueAnalytics(client)

print("Top Half Scorers by Week:")
analytics.print_weekly_top_half_scorers(league_id)

# client.get_player_fields()

# league = client.get_league("1048308938824937472")
# print(league.name)



""" 
# Print the player names and projections
projections = client.get_projections(2024, 1, "RB")

# Sort projections by pts_ppr in descending order
sorted_projections = sorted(projections, key=lambda p: p.stats.pts_ppr, reverse=True)
counter = 0
for projection in sorted_projections:
    counter += 1
    if counter > 30:
        break
    # Skip players with 0 projected pts_ppr
    if projection.stats.pts_ppr == 0:
        continue

    print(f"Player ID: {projection.player.player_id}")
    print(f"Name: {projection.player.first_name} {projection.player.last_name}")
    print(f"Team: {projection.player.team}")
    print(f"Opponent: {projection.opponent}")
    print("Projections:")
    print(f"  PPR Points: {projection.stats.pts_ppr:.2f}")
    print(f"  Rush Att: {projection.stats.rush_att:.1f}")
    print(f"  Rush Yards: {projection.stats.rush_yd:.1f}")
    print(f"  Rush TDs: {projection.stats.rush_td:.1f}")
    print(f"  Receptions: {projection.stats.rec:.1f}")
    print(f"  Rec Yards: {projection.stats.rec_yd:.1f}")
    print(f"  Rec TDs: {projection.stats.rec_td:.1f}")
    print("---")
"""



# client.print_weekly_matchups(league_id)
# client.print_league_rosters(league_id)
# client.get_matchups(league_id)

# print the matchups



# basic_league = client.get_league(league_id)
# print(f"Basic League Info: {basic_league.name}")

# Fetch all league info including teams and rosters
# full_league = client.get_league(league_id, fetch_all=True)
# print(f"\nFull League Info: {full_league.name}")
# for team in full_league.teams:
#     print(f"Team: {team.display_name} ({team.team_name})")
#     if team.roster:
#         print(f"  Players: {len(team.roster.players)}")
#         print(f"  Wins: {team.roster.wins}, Losses: {team.roster.losses}")
#     print("---")

# x = client.print_team_fields(league_id)
# teams = client.get_league_users(league_id)

# for team in teams:
#     print(team)

# rosters = client.get_league_rosters(league_id)

# for roster in rosters:
#     print(f"Roster ID: {roster.roster_id}")
#     print(f"Owner ID: {roster.owner_id}")
#     print(f"Players: {len(roster.players)}")
#     print(f"Starters: {len(roster.starters)}")
#     print(f"Wins: {roster.wins}, Losses: {roster.losses}, Ties: {roster.ties}")
#     print(f"Waiver Position: {roster.waiver_position}")
#     print(f"Waiver Budget Used: {roster.waiver_budget_used}")
#     print("---")

# players = client.get_players()
# client.save_players_to_file()

# for player_id, player in players.items():
#     print(player.name)
