from client import SleeperAPI

client = SleeperAPI()

# client.get_player_fields()

# league = client.get_league("1048308938824937472")
# print(league.name)

league_id = "1048308938824937472"

client.print_weekly_matchups(league_id)
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
