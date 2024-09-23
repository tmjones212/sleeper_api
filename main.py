from client import SleeperAPI
from league_analytics import LeagueAnalytics
from draft_kings_api import DraftKingsAPI
import os
import webbrowser


def generate_trade_html(trades_data, client):
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>League Trades</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; margin: 0 auto; background-color: #f0f0f0; }
            h1 { color: #333; text-align: center; }
            .trade-container { max-width: 1200px; margin: 0 auto; }
            .trade { background-color: #fff; border: 1px solid #ddd; padding: 15px; margin-bottom: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .trade-header { font-weight: bold; margin-bottom: 10px; font-size: 1.1em; color: #444; }
            .asset { margin-bottom: 15px; display: flex; align-items: center; }
            .team { flex: 0 0 200px; padding: 5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
            .arrow { flex: 0 0 30px; text-align: center; font-size: 1.2em; color: #666; }
            .player-img { width: 50px; height: 50px; border-radius: 50%; margin-right: 10px; object-fit: cover; }
            .asset-details { display: flex; align-items: center; flex: 1; }
            .asset-name { font-weight: bold; }
            .original-owner { font-style: italic; color: #666; margin-left: 10px; }
        </style>
    </head>
    <body>
        <div class="trade-container">
            <h1>League Trades</h1>
    """

    for trade in trades_data:
        html_content += f"""
        <div class="trade">
            <div class="trade-header">Week {trade['week']} - Trade ID: {trade['transaction_id']}</div>
        """
        for asset in trade['assets']:
            player_id = asset.get('player_id', '')
            img_url = f"https://sleepercdn.com/content/nfl/players/{player_id}.jpg" if player_id else ""
            img_tag = f'<img src="{img_url}" class="player-img" onerror="this.src=\'https://sleepercdn.com/images/v2/icons/player_default.webp\';">' if player_id else ""
            
            original_owner = ""
            if 'draft_pick' in asset:
                original_owner_id = asset['draft_pick']['roster_id']
                original_owner_name = client.get_team_name(trade['league_id'], original_owner_id)
                original_owner = f" <span class='original-owner'>(Original owner: {original_owner_name})</span>"
            
            html_content += f"""
            <div class="asset">
                <div class="team">{asset['old_team']}</div>
                <div class="arrow">&rarr;</div>
                <div class="team">{asset['new_team']}</div>
                <div class="asset-details">
                    {img_tag}
                    <span class="asset-name">{asset['asset']}{original_owner}</span>
                </div>
            </div>
            """
        html_content += "</div>"

    html_content += """
        </div>
    </body>
    </html>
    """

    file_path = 'league_trades.html'
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"HTML file generated: {os.path.abspath(file_path)}")
    
    # Open the generated HTML file in the default web browser
    webbrowser.open('file://' + os.path.realpath(file_path))




# ... (rest of the existing code)


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

league_id = "1048308938824937472" # 2024
# league_id = "916445745966915584" # 2023

client = SleeperAPI()
analytics = LeagueAnalytics(client)

# positions = ["QB", "RB", "WR", "TE"]  # Add or remove positions as needed
# year = 2024
# week = 1

week = 2

# Get all transactions for the week
transactions = client.get_league_transactions(league_id, week)

print("Year|Week|TransactionID|Asset|OldTeam|NewTeam")

current_year = client.get_current_season_year()
total_weeks = 4  # Assuming a standard NFL season

all_trades = []

for week in range(1, total_weeks + 1):
    transactions = client.get_league_transactions(league_id, week)
    
    for transaction in transactions:
        # Only process transactions of type "trade"
        if transaction.type != "trade":
            continue

        trade_data = {
            'week': week,
            'transaction_id': transaction.transaction_id,
            'league_id': league_id,
            'assets': []
        }

        # Process player adds
        if transaction.adds:
            for player_id, new_roster_id in transaction.adds.items():
                player_name = client.get_player_name(player_id)
                new_team = client.get_team_name(league_id, new_roster_id)
                old_team = "FA"  # Assume player was a free agent if not in drops
                if transaction.drops and player_id in transaction.drops:
                    old_team = client.get_team_name(league_id, transaction.drops[player_id])
                trade_data['assets'].append({
                    'asset': player_name,
                    'old_team': old_team,
                    'new_team': new_team,
                    'player_id': player_id
                })
        
        # Process draft picks
        if transaction.draft_picks:
            for pick in transaction.draft_picks:
                original_owner = client.get_team_name(league_id, pick.roster_id)
                asset = f"Round {pick.round} {pick.season} Pick"
                old_team = client.get_team_name(league_id, pick.previous_owner_id)
                new_team = client.get_team_name(league_id, pick.owner_id)
                trade_data['assets'].append({
                    'asset': asset,
                    'old_team': old_team,
                    'new_team': new_team,
                    'draft_pick': pick.__dict__
                })
        
        # Process FAAB
        if transaction.waiver_budget:
            for faab in transaction.waiver_budget:
                asset = f"${faab['amount']} FAAB"
                old_team = client.get_team_name(league_id, faab['sender'])
                new_team = client.get_team_name(league_id, faab['receiver'])
                trade_data['assets'].append({
                    'asset': asset,
                    'old_team': old_team,
                    'new_team': new_team
                })

        all_trades.append(trade_data)

# Generate HTML file
generate_trade_html(all_trades, client)


# for position in positions:
#     projections = client.get_projections(year, week, position)
#     print(f"Loaded {len(projections)} projections for {position}")

# projections = client.get_projections(2024, 1, "RB")
# print("Season Best Ball Total for All Teams:")
analytics.print_season_best_ball_total(league_id)

# analytics.print_league_standings(league_id)

# print("Season Best Ball Total for All Teams:")
# analytics.print_season_best_ball_total(league_id)
# projections = client.get_projections(2024, 1, "RB")
# print("\nWeekly Best Ball Scores for All Teams:")
# print(analytics.get_best_ball_scores(league_id,1))
# analytics.print_weekly_best_ball_scores(league_id)

print("\nWeekly Best Ball Scores for a Specific Team:")
team_name = "tmjones212"
# analytics.print_weekly_best_ball_scores(league_id, team_name)

# print("\n\nSeason Best Ball Total for a Specific Team:")
# team_name = "tmjones212"
analytics.print_season_best_ball_total(league_id)


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

