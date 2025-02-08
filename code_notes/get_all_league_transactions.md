---
description: Get all transactions for a league, starting from week 1 until no more transactions are found. Args: league_id (str): The league ID Returns: List[Dict[str, Any]]: List of all transactions with week number and datetime fields added
---

# get_all_league_transactions

**File:** league_analytics.py

## Description

Get all transactions for a league, starting from week 1 until no more transactions are found. Args: league_id (str): The league ID Returns: List[Dict[str, Any]]: List of all transactions with week number and datetime fields added

## Calls

- [[get_league_transactions]]

## Called By

- [[LeagueAnalytics.load_league_transactions]]
- [[load_league_transactions]]

