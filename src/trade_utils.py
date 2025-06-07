from typing import Dict, List

def print_player_trade_counts(trade_counts: Dict[str, int]) -> None:
    """
    Print a formatted list of players and their trade counts.
    """
    print("\nPlayer Trade Counts:")
    print("-" * 40)
    for player, count in trade_counts.items():
        print(f"{player}: {count} trades")

def print_player_trade_history(trades: List[Dict]) -> None:
    """
    Print detailed trade history for a player in a readable format.
    """
    for trade in trades:
        print(f"\nTrade on {trade['date']}:")
        for team, received in trade['teams'].items():
            print(f"\n{team} received:")
            if received['players']:
                print("  Players:")
                for player in received['players']:
                    print(f"    {player}")
            if received['picks']:
                print("  Draft Picks:")
                for pick in received['picks']:
                    print(f"    {pick}")
        print("-" * 50)

def print_manager_trade_history(trades: List[Dict], manager_name: str) -> None:
    """
    Print detailed trade history for a manager in a readable format.
    """
    print(f"\nTrade History for {manager_name}:")
    print("=" * 50)
    
    for trade in trades:
        print(f"\nTrade on {trade['date']}:")
        
        # Print received items
        print("\nReceived:")
        for move in trade['received']['players']:
            print(f"  {move['player']} to {move['team']}")
        for pick in trade['received']['draft_picks']:
            print(f"  {pick['season']} Round {pick['round']} from {pick['from_team']} to {pick['to_team']}")
        
        # Print given items
        print("\nGiven:")
        for move in trade['given']['players']:
            print(f"  {move['player']} from {move['team']}")
        for pick in trade['given']['draft_picks']:
            print(f"  {pick['season']} Round {pick['round']} from {pick['from_team']} to {pick['to_team']}")
        
        print("-" * 50) 