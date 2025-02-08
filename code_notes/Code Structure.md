# Code Structure

## client.py

### Classes

- [[SleeperAPI]]
- [[__init__]]
- [[_associate_rosters_with_teams]]
- [[_calculate_fantasy_points]]
- [[_get_week_ranges]]
- [[_make_request]]
- [[_print_player]]
- [[_reconstruct_player_projection]]
- [[clear_cache]]
- [[fetch_players_from_api]]
- [[format_player_name]]
- [[get_all_matchups]]
- [[get_current_season_year]]
- [[get_current_week]]
- [[get_league]]
- [[get_league_rosters]]
- [[get_league_transactions]]
- [[get_league_users]]
- [[get_matchups]]
- [[get_player_fields]]
- [[get_player_name]]
- [[get_player_position]]
- [[get_projections]]
- [[get_stats]]
- [[load_cache]]
- [[load_matchups_cache]]
- [[load_players_from_file]]
- [[load_projections_cache]]
- [[load_stats_cache]]
- [[print_league_rosters]]
- [[print_team_fields]]
- [[save_cache]]
- [[save_matchups_cache]]
- [[save_players_to_file]]
- [[save_projections_cache]]
- [[save_stats_cache]]

## code_flow.py

### Classes

- [[CodeAnalyzer]]
- [[__init__]]
- [[_process_class]]
- [[_process_function]]
- [[analyze_directory]]
- [[analyze_file]]
- [[create_flow_diagram]]
- [[export_to_obsidian]]

## customer_json_encoder.py

### Classes

- [[CustomJSONEncoder]]
- [[default]]

## draft_kings_api.py

### Classes

- [[DraftKingsAPI]]
- [[extract_player_props]]
- [[get_all_subcategories]]
- [[get_nfl_player_props]]
- [[get_nfl_player_props_2]]
- [[get_subcategory_id]]

## exceptions.py

### Classes

- [[SleeperAPIException]]

## league_analytics.py

### Classes

- [[LeagueAnalytics]]
- [[__init__]]
- [[_calculate_actual_points]]
- [[_calculate_best_ball_points]]
- [[_calculate_offensive_best_ball_points]]
- [[add_to_lineup]]
- [[get_all_league_transactions]]
- [[get_best_ball_scores]]
- [[get_league_standings]]
- [[get_player_stats]]
- [[get_season_best_ball_total]]
- [[get_team_best_ball]]
- [[get_top_half_scorers]]
- [[get_weekly_best_ball_scores]]
- [[get_weekly_drops]]
- [[is_offensive_position]]
- [[is_time_in_range]]
- [[load_league_transactions]]
- [[players_dropped_before_waivers_cleared]]
- [[print_league_standings]]
- [[print_season_best_ball_total]]
- [[print_team_best_ball]]
- [[print_weekly_best_ball_scores]]
- [[print_weekly_top_half_scorers]]
- [[write_offensive_best_ball_to_csv]]

## league_helper.py

## main.py

## models.py

### Classes

- [[League]]
- [[LeagueMetadata]]
- [[LeagueSettings]]
- [[Matchup]]
- [[Player]]
- [[PlayerInfo]]
- [[PlayerProjection]]
- [[PlayerProp]]
- [[PlayerStats]]
- [[ProjectedStats]]
- [[Roster]]
- [[SleeperProjections]]
- [[Team]]
- [[Transaction]]
- [[__init__]]
- [[__post_init__]]
- [[__repr__]]
- [[__str__]]
- [[format_name]]
- [[from_dict]]
- [[get_projections]]
- [[team_name]]

## player_extensions.py

### Classes

- [[format_name]]

## sleeper_api_calls.py

### Classes

- [[get_player_stats_from_api]]

## sleeper_data_puller.py

