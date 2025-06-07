#!/usr/bin/env python3
"""
Debug the float error in trade visualization
"""
import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from client import SleeperAPI

def debug_float_error():
    """Debug the float error"""
    print("🔍 Debugging Float Error")
    print("=" * 50)
    
    try:
        # Initialize API
        league_id = "1048308938824937472"
        api = SleeperAPI(league_id)
        
        print("✅ API initialized successfully")
        
        # Test network data generation
        print("Testing network data generation...")
        network_data = api.trade_visualization_service.get_trade_network_data(league_id)
        print(f"✅ Network data generated: {len(network_data['nodes'])} nodes, {len(network_data['edges'])} edges")
        
        # Test timeline data generation
        print("Testing timeline data generation...")
        timeline_data = api.trade_visualization_service.get_league_trade_timeline(league_id)
        print(f"✅ Timeline data generated: {len(timeline_data['trades'])} trades")
        
        # Test trade matrix generation
        print("Testing trade matrix generation...")
        trade_matrix = api.trade_visualization_service.get_team_trade_matrix(league_id)
        print(f"✅ Trade matrix generated: {len(trade_matrix['teams'])} teams")
        
        # Test HTML generation (this is where the error likely occurs)
        print("Testing HTML generation...")
        html_content = api.trade_visualization_service.generate_trade_visualization_html(league_id)
        print(f"✅ HTML generated successfully: {len(html_content)} characters")
        
        print("\n🎉 All tests passed - no float error detected!")
        
    except Exception as e:
        print(f"❌ Error found: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        
        # Try to isolate the issue
        if "'float' object is not iterable" in str(e):
            print("\n🔍 Investigating float iteration error...")
            print("This typically happens when code expects a list/dict but gets a float")

if __name__ == "__main__":
    debug_float_error()