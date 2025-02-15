from datetime import datetime
from client import SleeperAPI
from league_analytics import LeagueAnalytics
from draft_kings_api import DraftKingsAPI
import json
from sleeper_api_calls import get_player_stats_from_api

# subcategories = DraftKingsAPI.get_all_subcategories()
# for sub in subcategories:
#     print(f"Name: {sub['name']}, ID: {sub['id']}")

# pass_yard_props = DraftKingsAPI.get_nfl_player_props_2("Passing Yards")

# rush_rec_yards_props = DraftKingsAPI.get_nfl_player_props(1, "Rush + Rec Yards")


# # Remove duplicates
# unique_props = {prop.player_name: prop for prop in rush_rec_yards_props}.values()

# # Sort props by player name
# sorted_props = sorted(unique_props, key=lambda x: x.player_name)

# # Print the props in a tabular format
# print("Name                 | PropName         | Value | OverLine | UnderLine")
# print("-" * 70)
# for prop in sorted_props:
#     print(f"{prop.player_name:<20} | {prop.prop_type:<16} | {prop.prop_value:>5} | {prop.over_line:>8} | {prop.under_line:>9}")

# 2024-10-16 01:39 PM - BRAYDEN NARVESON dropped by Halteclere

league_id = "1048308938824937472" # 2024
# league_id = "916445745966915584" # 2023

client = SleeperAPI()
analytics = LeagueAnalytics(client)

year = 2024
positions = ["QB", "RB", "WR", "TE",'DB']

rosters = client.league_manager.get_league_rosters(league_id)

transactions = analytics.get_all_league_transactions(league_id)

for transaction in transactions:
	d = 2
	print(transaction)

# for position in positions:
# 	for week in range(1,18):
# 		stats = analytics.get_player_stats_from_api(year, week, position)
# 		# Print stats in JSON format
# 		print(json.dumps(stats, indent=4))
# 		# Convert stats objects to dictionaries
# 		stats_dict = {player_id: stat.__dict__ for player_id, stat in stats.items()}
# 		# Create filename with the specified pattern
# 		filename = f"{year}_Week_{week}_{position}.json"
# 		# Write stats to JSON file
# 		with open(filename, 'w') as f:
# 			json.dump(stats_dict, f, indent=4)


# print(stats)
# print('---')


# league = client.get_league(league_id, fetch_all=True)
# week = 7

# transactions = analytics.get_all_league_transactions(league_id)
# transactions = [x for x in analytics.load_league_transactions(league_id) if x['status'] == "complete" and x['type'] == "waiver" and x['week'] == 10]
# dates = [x['datetime'] for x in transactions]
# print(dates)
# drops = analytics.get_weekly_drops(league_id, week)
# for drop in drops:
#     if drop['player_name'].lower() == "brayden narveson":
#         print(f"{drop['dropped_at']} - {drop['player_name']} dropped by {drop['team_name']}")

#dropped_players = analytics.players_dropped_before_waivers_cleared(league_id, week)
# print(dropped_players)

# transactions = client.get_league_transactions(league_id, week)
# team_names = {team.roster.roster_id: team.display_name for team in league.teams if team.roster}

# for transaction in transactions:
#     # Only process transactions that have drops but no adds
#     if transaction['drops'] and not transaction['adds']:
#         transaction_time = datetime.fromtimestamp(transaction['created'] / 1000)
#         formatted_time = transaction_time.strftime('%Y-%m-%d %I:%M %p')
		
#         print(f"Drop Transaction {transaction['transaction_id']} ({formatted_time}):")
#         print(f"  Status: {transaction['status']}")
#         print("  Drops:")
#         for player_id, roster_id in transaction['drops'].items():
#             player_name = client.get_player_name(player_id)
#             team_name = team_names.get(roster_id, f"Team {roster_id}")
#             print(f"    {player_name} from {team_name}")
#         print("---")

# for transaction in transactions:
#     if transaction['type'] == 'waiver':
#         # Convert Unix timestamp (milliseconds) to datetime
#         transaction_time = datetime.fromtimestamp(transaction['created'] / 1000)
#         formatted_time = transaction_time.strftime('%Y-%m-%d %I:%M %p')
		
#         print(f"Waiver Transaction {transaction['transaction_id']} ({formatted_time}):")
#         print(f"  Status: {transaction['status']}")
#         if transaction['adds']:
#             print("  Adds:")
#             for player_id, roster_id in transaction['adds'].items():
#                 player_name = client.get_player_name(player_id)
#                 team_name = team_names.get(roster_id, f"Team {roster_id}")
#                 print(f"    {player_name} to {team_name}")
#         if transaction['drops']:
#             print("  Drops:")
#             for player_id, roster_id in transaction['drops'].items():
#                 player_name = client.get_player_name(player_id)
#                 team_name = team_names.get(roster_id, f"Team {roster_id}")
#                 print(f"    {player_name} from {team_name}")
#         print("---")

		
# positions = ["QB", "RB", "WR", "TE"]  # Add or remove positions as needed
# year = 2024
# week = 1

# for position in positions:
#     projections = client.get_projections(year, week, position)
#     print(f"Loaded {len(projections)} projections for {position}")

# projections = client.get_projections(2024, 1, "RB")
# print("Season Best Ball Total for All Teams:")
# analytics.print_season_best_ball_total(league_id)


# analytics.write_offensive_best_ball_to_csv(league_id)

# print("Season Best Ball Total for All Teams:")
# analytics.print_season_best_ball_total(league_id)
# projections = client.get_projections(2024, 1, "RB")
# print("\nWeekly Best Ball Scores for All Teams:")
# print(analytics.get_best_ball_scores(league_id,1))
# analytics.print_weekly_best_ball_scores(league_id)


# print("\nWeekly Best Ball Scores for a Specific Team:")
# team_name = "tmjones212"
# analytics.print_weekly_best_ball_scores(league_id, team_name)

# print("\n\nSeason Best Ball Total for a Specific Team:")
# team_name = "tmjones212"


analytics.print_league_standings(league_id) # this gets the real standings I think
# analytics.print_season_best_ball_total(league_id)


# team_name = "tmjones212"
# week = 1

# print(f"Best Ball for {team_name} in Week {week}:")
# analytics.print_team_best_ball(league_id, team_name, week)


# print("Top Half Scorers by Week:")
# analytics.print_weekly_top_half_scorers(league_id)

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
