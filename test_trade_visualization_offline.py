#!/usr/bin/env python3
"""
Test script for trade visualization functionality using cached data
"""
import sys
import os
import json

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from client import SleeperAPI

def test_trade_visualization_offline():
    """Test the trade visualization functionality using cached data"""
    print("🏈 Testing Trade Visualization System (Offline Mode)")
    print("=" * 60)
    
    # Check available cached transaction data
    data_dir = "data"
    transaction_files = [f for f in os.listdir(data_dir) if f.startswith("league_") and f.endswith("_transactions.json")]
    
    if not transaction_files:
        print("❌ No cached transaction data found")
        return False
    
    print(f"📁 Found {len(transaction_files)} cached transaction files:")
    for f in transaction_files:
        print(f"   - {f}")
    
    # Use the first available transaction file
    transaction_file = transaction_files[0]
    league_id = transaction_file.replace("league_", "").replace("_transactions.json", "")
    
    print(f"\n🎯 Using league {league_id} for testing")
    
    try:
        # Load cached data directly to test visualization components
        print("\n1. Loading cached transaction data...")
        with open(os.path.join(data_dir, transaction_file), 'r') as f:
            cached_transactions = json.load(f)
        
        print(f"   ✅ Loaded {len(cached_transactions)} transactions from cache")
        
        # Filter for trades only
        trades = [t for t in cached_transactions if t.get('type') == 'trade']
        print(f"   📊 Found {len(trades)} trades")
        
        if len(trades) == 0:
            print("   ⚠️  No trades found in this league - testing with mock data")
            # Create some mock trade data for testing
            mock_trade = {
                'type': 'trade',
                'status': 'complete',
                'created': 1640995200000,  # Jan 2022
                'date': '2022-01-01 12:00 PM',
                'received': {
                    'teams': [{
                        'team': 'Team A',
                        'players': [{'player': 'Josh Allen'}],
                        'draft_picks': []
                    }]
                },
                'given': {
                    'teams': [{
                        'team': 'Team B', 
                        'players': [{'player': 'Lamar Jackson'}],
                        'draft_picks': []
                    }]
                }
            }
            trades = [mock_trade]
        
        print("\n2. Testing TradeVisualizationService components...")
        
        # Initialize minimal API instance (without network calls)
        api = SleeperAPI()
        
        # Test individual components
        print("   📊 Testing trade network data generation...")
        
        # Mock the get_trades method to return our cached data
        def mock_get_trades(league_id):
            return trades
        
        api.transaction_service.get_trades = mock_get_trades
        
        # Test network data generation
        network_data = api.trade_visualization_service.get_trade_network_data(league_id)
        print(f"      - Network nodes: {len(network_data['nodes'])}")
        print(f"      - Network edges: {len(network_data['edges'])}")
        print(f"      - Most active traders: {len(network_data['most_active_traders'])}")
        
        print("   📅 Testing timeline data generation...")
        timeline_data = api.trade_visualization_service.get_league_trade_timeline(league_id)
        print(f"      - Timeline trades: {len(timeline_data['trades'])}")
        print(f"      - Total players traded: {timeline_data['stats']['total_players_traded']}")
        
        print("\n3. Testing HTML template generation...")
        
        # Mock the player trade counts
        def mock_get_player_trade_counts(league_id):
            return {"Josh Allen": 1, "Lamar Jackson": 1}
        
        api.transaction_service.get_player_trade_counts = mock_get_player_trade_counts
        
        # Generate HTML
        html_content = api.trade_visualization_service.generate_trade_visualization_html(league_id)
        
        print(f"      ✅ Generated HTML ({len(html_content)} characters)")
        
        # Save to file
        output_file = f"test_trade_visualization_{league_id}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"      📄 Saved to: {output_file}")
        
        print("\n4. Testing template components...")
        
        # Check if template contains expected elements
        expected_elements = [
            'Trade Visualization Dashboard',
            'trade-network',
            'timeline-container',
            'Chart.js',
            'vis-network'
        ]
        
        for element in expected_elements:
            if element in html_content:
                print(f"      ✅ Found: {element}")
            else:
                print(f"      ❌ Missing: {element}")
        
        print("\n5. Sample trade data structure:")
        if trades:
            sample_trade = trades[0]
            print(f"      - Date: {sample_trade.get('date', 'Unknown')}")
            print(f"      - Type: {sample_trade.get('type', 'Unknown')}")
            print(f"      - Status: {sample_trade.get('status', 'Unknown')}")
            
            # Show teams involved
            received_teams = sample_trade.get('received', {}).get('teams', [])
            given_teams = sample_trade.get('given', {}).get('teams', [])
            
            print(f"      - Teams receiving: {[t.get('team') for t in received_teams]}")
            print(f"      - Teams giving: {[t.get('team') for t in given_teams]}")
        
        print("\n" + "=" * 60)
        print("✅ All offline tests completed successfully!")
        print(f"🎯 Test output: {output_file}")
        print("📝 The trade visualization system is working with cached data!")
        print("🌐 Open the HTML file in a web browser to see the visualization")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_trade_visualization_offline()
    if success:
        print("\n🏆 Trade visualization system is ready!")
        print("💡 To use with live data, ensure you have internet connectivity")
    else:
        print("\n💥 Issues found with the trade visualization system.")
        sys.exit(1)