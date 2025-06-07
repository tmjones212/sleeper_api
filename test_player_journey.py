#!/usr/bin/env python3
"""
Test the comprehensive player journey functionality
"""
import sys
import os
import json

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from client import SleeperAPI

def test_player_journey():
    """Test the player journey tracking functionality"""
    print("🔧 Testing Player Journey Functionality")
    print("=" * 60)
    
    try:
        # Initialize API
        league_id = "1181025001438806016"  # Latest league
        api = SleeperAPI(league_id)
        
        # Test with Jerry Jeudy - we know he was traded
        player_name = "Jerry Jeudy"
        print(f"📋 Testing player journey for: {player_name}")
        
        journey_data = api.get_player_trade_journey(player_name, league_id)
        
        print(f"\n✅ Player Journey Data Retrieved:")
        print(f"Player Name: {journey_data['player_name']}")
        print(f"Total Trades: {journey_data['total_trades']}")
        print(f"Current Team: {journey_data.get('current_team', 'Unknown')}")
        print(f"Teams Involved: {journey_data['teams_involved']}")
        print(f"Timeline Events: {len(journey_data['timeline'])}")
        
        if journey_data['timeline']:
            print(f"\n📅 Timeline Events:")
            for i, event in enumerate(journey_data['timeline'][:5]):  # Show first 5 events
                print(f"  {i+1}. {event['date']} - {event['type']}")
                if event['type'] == 'trade':
                    print(f"     {event['from_team']} → {event['to_team']}")
                elif event['type'] in ['free_agent', 'waiver']:
                    print(f"     {event['from_team']} → {event['to_team']}")
        
        print(f"\n🎉 Player journey test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_players():
    """Test journey for multiple players"""
    print("\n🔧 Testing Multiple Player Journeys")
    print("=" * 60)
    
    try:
        league_id = "1181025001438806016"  # Latest league
        api = SleeperAPI(league_id)
        
        # Get most traded players for testing
        player_counts = api.transaction_service.get_player_trade_counts(league_id)
        most_traded = list(player_counts.keys())[:3]  # Top 3 most traded
        
        print(f"Testing top 3 most traded players: {most_traded}")
        
        for player_name in most_traded:
            print(f"\n📊 {player_name}:")
            journey = api.get_player_trade_journey(player_name, league_id)
            print(f"  Trades: {journey['total_trades']}, Timeline Events: {len(journey['timeline'])}")
            if journey['timeline']:
                print(f"  First event: {journey['timeline'][0]['date']} - {journey['timeline'][0]['type']}")
                print(f"  Last event: {journey['timeline'][-1]['date']} - {journey['timeline'][-1]['type']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success1 = test_player_journey()
    success2 = test_multiple_players()
    
    if success1 and success2:
        print(f"\n✅ All player journey tests passed!")
    else:
        print(f"\n❌ Some player journey tests failed!")
        sys.exit(1)