from player_extensions import format_name
import requests

STATS_ENDPOINT = "https://api.sleeper.app/v1"

def get_player_stats_from_api(year: int, week: int, position: str) -> dict:
    """Get stats for all players for a specific week."""
    # Get stats data
    stats_url = f"{STATS_ENDPOINT}/stats/nfl/regular/{year}/{week}"
    stats_response = requests.get(stats_url)
    stats_response.raise_for_status()
    stats_data = stats_response.json()
    
    # Get players data
    players_url = f"{STATS_ENDPOINT}/players/nfl"
    players_response = requests.get(players_url)
    players_response.raise_for_status()
    players_data = players_response.json()
    
    stat_records = []
    
    for player_id, stats in stats_data.items():
        player_info = players_data.get(player_id, {})
        if player_info.get('position') == position:
            stat_record = {
                "player": {
                    "years_exp": player_info.get("years_exp"),
                    "team": player_info.get("team"),
                    "position": position,
                    "news_updated": player_info.get("news_updated"),
                    "metadata": {
                        "rookie_year": player_info.get("rookie_year")
                    },
                    "last_name": player_info.get("last_name"),
                    "injury_status": player_info.get("injury_status"),
                    "injury_start_date": player_info.get("injury_start_date"),
                    "injury_notes": player_info.get("injury_notes"),
                    "injury_body_part": player_info.get("injury_body_part"),
                    "first_name": player_info.get("first_name"),
                    "fantasy_positions": [position]
                },
                "opponent": stats.get("opponent"),
                "company": "sportradar",
                "team": player_info.get("team"),
                "game_id": stats.get("game_id"),
                "player_id": player_id,
                "sport": "nfl",
                "season_type": "regular",
                "season": str(year),
                "week": week,
                "last_modified": stats.get("last_modified"),
                "category": "stat",
                "stats": stats,
                "date": stats.get("date")
            }
            stat_records.append(stat_record)
    
    return {"statRecords": stat_records}

