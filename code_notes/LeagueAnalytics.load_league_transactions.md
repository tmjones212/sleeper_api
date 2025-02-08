---
description: Load transactions from the JSON file for a given league. If the file doesn't exist, fetch and create it. Args: league_id (str): The league ID Returns: List[Dict[str, Any]]: List of all transactions with week numbers
---

# load_league_transactions

**File:** league_analytics.py
**Class:** [[LeagueAnalytics]]

## Description

Load transactions from the JSON file for a given league. If the file doesn't exist, fetch and create it. Args: league_id (str): The league ID Returns: List[Dict[str, Any]]: List of all transactions with week numbers

## Calls

- [[SleeperAPIException]]
- [[get_all_league_transactions]]

