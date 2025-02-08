---
description: Get all players dropped between Sunday 5 PM and Wednesday 9 AM for a specific week. Args: league_id (str): The league ID week (int): The week number to check Returns: List[Dict[str, str]]: List of dictionaries containing player_name and team_name
---

# players_dropped_before_waivers_cleared

**File:** league_analytics.py

## Description

Get all players dropped between Sunday 5 PM and Wednesday 9 AM for a specific week. Args: league_id (str): The league ID week (int): The week number to check Returns: List[Dict[str, str]]: List of dictionaries containing player_name and team_name

## Calls

- [[get_league]]
- [[get_league_transactions]]
- [[get_player_name]]
- [[is_time_in_range]]

