#!/usr/bin/env python3
"""
Test script for trade visualization functionality
"""
import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from client import SleeperAPI

def test_trade_visualization():
    """Test the trade visualization functionality"""
    print("🏈 Testing Trade Visualization System")
    print("=" * 50)
    
    # Initialize the API client
    # Using one of the leagues from the data files
    league_id = "1048308938824937472"  # From the data directory
    
    try:
        print(f"Initializing SleeperAPI for league {league_id}...")
        api = SleeperAPI(league_id)
        
        print("\n1. Testing Trade Network Analysis...")
        network_data = api.get_trade_network_analysis()
        print(f"   - Found {len(network_data['nodes'])} teams in trade network")
        print(f"   - Found {len(network_data['edges'])} trade relationships")
        
        if network_data['most_active_traders']:
            print("   - Most active traders:")
            for i, (team_name, team_data) in enumerate(network_data['most_active_traders'][:3]):
                print(f"     {i+1}. {team_name}: {team_data['trade_count']} trades")
        
        print("\n2. Testing Player Trade Journey...")
        # Get most traded players first
        player_counts = api.transaction_service.get_player_trade_counts(league_id)
        if player_counts:
            most_traded_player = max(player_counts.items(), key=lambda x: x[1])
            player_name, trade_count = most_traded_player
            
            print(f"   - Tracking journey for most traded player: {player_name} ({trade_count} trades)")
            journey = api.get_player_trade_journey(player_name)
            
            print(f"     * Total trades: {journey['total_trades']}")
            print(f"     * Teams involved: {', '.join(journey['teams_involved'])}")
            print(f"     * Current team: {journey.get('current_team', 'Unknown')}")
        else:
            print("   - No player trade data found")
        
        print("\n3. Generating Trade Visualization HTML...")
        output_file = f"trade_visualization_test_{league_id}.html"
        result_path = api.generate_trade_visualization(output_file=output_file)
        
        print(f"   ✅ Trade visualization generated successfully!")
        print(f"   📄 Output file: {result_path}")
        print(f"   🌐 Open this file in your browser to view the interactive visualization")
        
        print("\n4. Testing Raw Data Access...")
        # Test some transaction service methods directly
        trades = api.transaction_service.get_trades(league_id)
        print(f"   - Found {len(trades)} total trades")
        
        # Show sample trade
        if trades:
            sample_trade = trades[0]
            print(f"   - Sample trade date: {sample_trade.get('date', 'Unknown')}")
            print(f"   - Teams involved: {sample_trade.get('teams_involved', [])}")
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        print(f"🎯 Main output: {result_path}")
        print("🚀 Open the HTML file in a web browser to explore your league's trades!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_trade_visualization()
    if success:
        print("\n🏆 Trade visualization system is ready to use!")
    else:
        print("\n💥 There were issues with the trade visualization system.")
        sys.exit(1)