---
description: Get all players dropped in a given week, including when they were dropped and by whom. Args: league_id (str): The league ID week (int): The week number to check Returns: List[Dict[str, str]]: List of dictionaries containing player_name, team_name, and dropped_at
---

# get_weekly_drops

**File:** league_analytics.py

## Description

Get all players dropped in a given week, including when they were dropped and by whom. Args: league_id (str): The league ID week (int): The week number to check Returns: List[Dict[str, str]]: List of dictionaries containing player_name, team_name, and dropped_at

## Calls

- [[get_league]]
- [[get_league_transactions]]
- [[get_player_name]]

