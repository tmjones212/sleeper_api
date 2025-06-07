#!/usr/bin/env python3
"""
Example script showing how to use the trade visualization system
"""
import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from client import SleeperAPI

def main():
    """Example usage of the trade visualization system"""
    print("🏈 Fantasy Football Trade Visualization")
    print("=" * 50)
    
    # Replace with your league ID
    league_id = "1048308938824937472"  # Example league ID
    
    try:
        # Initialize the API client
        print(f"Initializing API for league {league_id}...")
        api = SleeperAPI(league_id)
        
        # Method 1: Generate complete trade visualization HTML
        print("\n📊 Generating complete trade visualization...")
        output_file = api.generate_trade_visualization()
        print(f"✅ Visualization saved to: {output_file}")
        
        # Method 2: Get specific trade data for analysis
        print("\n📈 Getting trade network analysis...")
        network_data = api.get_trade_network_analysis()
        
        print(f"Found {len(network_data['nodes'])} teams in trade network")
        print(f"Found {len(network_data['edges'])} trade relationships")
        
        if network_data['most_active_traders']:
            print("\nMost Active Traders:")
            for i, (team_name, team_data) in enumerate(network_data['most_active_traders'][:3]):
                print(f"  {i+1}. {team_name}: {team_data['trade_count']} trades")
        
        # Method 3: Track a specific player's journey
        print("\n👤 Example: Track a player's trade journey...")
        
        # Get most traded players
        player_counts = api.transaction_service.get_player_trade_counts(league_id)
        if player_counts:
            # Get the most traded player
            most_traded_player = max(player_counts.items(), key=lambda x: x[1])
            player_name, trade_count = most_traded_player
            
            print(f"Tracking {player_name} ({trade_count} trades)...")
            journey = api.get_player_trade_journey(player_name)
            
            print(f"  • Total trades: {journey['total_trades']}")
            print(f"  • Teams: {', '.join(journey['teams_involved'])}")
            print(f"  • Current team: {journey.get('current_team', 'Unknown')}")
            
            # Show trade timeline
            if journey['timeline']:
                print("\n  Trade Timeline:")
                for i, trade in enumerate(journey['timeline'][:3]):  # Show first 3
                    from_team = trade['from_team'] or 'Initial Team'
                    to_team = trade['to_team'] or 'Unknown'
                    print(f"    {i+1}. {trade['date']}: {from_team} → {to_team}")
        
        print(f"\n🌐 Open {output_file} in your web browser to explore!")
        print("\nFeatures in the visualization:")
        print("  📊 Overview - League trading statistics")
        print("  🕸️ Network - Interactive team relationship graph")
        print("  📅 Timeline - Chronological view of all trades")
        print("  👤 Player Journey - Search and track individual players")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Make sure you have internet connectivity")
        print("2. Verify your league ID is correct")
        print("3. Check that the league has trading activity")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)