#!/usr/bin/env python3
"""
Test script to validate trade logic and ensure no identical assets on both sides
"""
import sys
import os
from collections import defaultdict

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from client import SleeperAPI

def test_trade_logic_validation():
    """Test trade logic to ensure no duplicate/identical assets on both sides"""
    print("🧪 Testing Trade Logic Validation")
    print("=" * 60)
    
    try:
        # Initialize API
        league_id = "1048308938824937472"
        api = SleeperAPI(league_id)
        
        # Get trades
        print("Loading trade data...")
        trades = api.transaction_service.get_trades(league_id)
        print(f"Found {len(trades)} trades to validate")
        
        # Validation counters
        validation_results = {
            'total_trades': len(trades),
            'passed_validation': 0,
            'failed_validation': 0,
            'identical_assets_errors': [],
            'empty_side_errors': [],
            'one_sided_errors': []
        }
        
        print("\n🔍 Running validation tests...")
        print("-" * 60)
        
        for i, trade in enumerate(trades):
            trade_date = trade.get('date', f'Trade #{i+1}')
            received_players = trade.get('received', {}).get('players', [])
            given_players = trade.get('given', {}).get('players', [])
            received_picks = trade.get('received', {}).get('draft_picks', [])
            
            # Test 1: Check for teams getting AND giving the same player (this would be wrong)
            # Same player can appear on both sides if different teams are involved
            team_player_combos_received = set((p['team'], p['player']) for p in received_players)
            team_player_combos_given = set((p['team'], p['player']) for p in given_players)
            identical_team_player_combos = team_player_combos_received.intersection(team_player_combos_given)
            
            if identical_team_player_combos:
                validation_results['failed_validation'] += 1
                validation_results['identical_assets_errors'].append({
                    'date': trade_date,
                    'identical_combos': list(identical_team_player_combos),
                    'trade': trade
                })
                print(f"❌ FAIL: {trade_date} - Team receiving AND giving same player: {identical_team_player_combos}")
                continue
            
            # Test 2: Check for empty sides (should have at least something on each side)
            has_received_assets = len(received_players) > 0 or len(received_picks) > 0
            has_given_assets = len(given_players) > 0
            
            if not has_received_assets or not has_given_assets:
                validation_results['failed_validation'] += 1
                validation_results['one_sided_errors'].append({
                    'date': trade_date,
                    'received_count': len(received_players) + len(received_picks),
                    'given_count': len(given_players),
                    'trade': trade
                })
                print(f"⚠️  WARN: {trade_date} - One-sided trade (R:{len(received_players) + len(received_picks)}, G:{len(given_players)})")
                continue
            
            # Test 3: Verify proper trade flow (for each player, if team A receives from team B, then team B should give to team A)
            trade_flows_valid = True
            for received_player in received_players:
                player_name = received_player['player']
                receiving_team = received_player['team']
                from_team = received_player.get('from_team')
                
                # Find the corresponding "given" entry
                corresponding_given = None
                for given_player in given_players:
                    if (given_player['player'] == player_name and 
                        given_player['team'] == from_team and
                        given_player.get('to_team') == receiving_team):
                        corresponding_given = given_player
                        break
                
                if not corresponding_given and from_team:
                    print(f"⚠️  {trade_date} - Missing corresponding 'given' for {player_name}: {receiving_team} receives from {from_team}")
                    trade_flows_valid = False
            
            # Test 4: Check that we don't have the same teams on both sides exclusively (would indicate duplicate processing)
            received_teams = set(p['team'] for p in received_players)
            given_teams = set(p['team'] for p in given_players)
            
            # It's OK to have overlap, but they shouldn't be identical sets
            if received_teams and given_teams and received_teams == given_teams and len(received_players) == len(given_players):
                # Additional check: make sure it's not just duplicated data
                received_players_sorted = sorted([(p['team'], p['player']) for p in received_players])
                given_players_sorted = sorted([(p['team'], p['player']) for p in given_players])
                if received_players_sorted == given_players_sorted:
                    print(f"⚠️  {trade_date} - Possible duplicate processing detected")
            
            validation_results['passed_validation'] += 1
            
            # Show first few successful trades
            if validation_results['passed_validation'] <= 3:
                print(f"✅ PASS: {trade_date}")
                print(f"   Received: {[p['player'] + ' to ' + p['team'] for p in received_players]}")
                print(f"   Given: {[p['player'] + ' from ' + p['team'] for p in given_players]}")
                if received_picks:
                    picks_desc = [f"{p['round']} round {p['season']}" for p in received_picks]
                    print(f"   Picks: {picks_desc}")
                print()
        
        # Print summary
        print("\n📋 VALIDATION SUMMARY")
        print("=" * 60)
        print(f"Total trades analyzed: {validation_results['total_trades']}")
        print(f"✅ Passed validation: {validation_results['passed_validation']}")
        print(f"❌ Failed validation: {validation_results['failed_validation']}")
        
        # Report specific errors
        if validation_results['identical_assets_errors']:
            print(f"\n🚨 CRITICAL: {len(validation_results['identical_assets_errors'])} trades with identical assets:")
            for error in validation_results['identical_assets_errors'][:5]:  # Show first 5
                print(f"   - {error['date']}: {error['identical_players']}")
        
        if validation_results['one_sided_errors']:
            print(f"\n⚠️  WARNING: {len(validation_results['one_sided_errors'])} one-sided trades:")
            for error in validation_results['one_sided_errors'][:5]:  # Show first 5
                print(f"   - {error['date']}: R:{error['received_count']}, G:{error['given_count']}")
        
        # Test specific known problematic trades
        print(f"\n🎯 SPECIFIC TRADE TESTS")
        print("-" * 40)
        
        # Look for Evan Hull trade mentioned by user
        hull_trades = []
        for trade in trades:
            all_players = (trade.get('received', {}).get('players', []) + 
                          trade.get('given', {}).get('players', []))
            for player in all_players:
                if 'EVAN HULL' in player.get('player', '').upper():
                    hull_trades.append(trade)
                    break
        
        if hull_trades:
            print(f"Found {len(hull_trades)} Evan Hull trades:")
            for trade in hull_trades[:2]:  # Check first 2
                print(f"Date: {trade.get('date')}")
                print(f"Received: {[p['player'] + ' to ' + p['team'] for p in trade.get('received', {}).get('players', [])]}")
                print(f"Given: {[p['player'] + ' from ' + p['team'] for p in trade.get('given', {}).get('players', [])]}")
                
                # Check for teams getting AND giving same player (this would be wrong)
                r_team_players = set((p['team'], p['player']) for p in trade.get('received', {}).get('players', []))
                g_team_players = set((p['team'], p['player']) for p in trade.get('given', {}).get('players', []))
                if r_team_players.intersection(g_team_players):
                    print("❌ ERROR: Same team receiving AND giving same player!")
                else:
                    print("✅ GOOD: Trade shows proper player flow between different teams")
                print()
        
        # Final assessment
        success_rate = (validation_results['passed_validation'] / validation_results['total_trades']) * 100
        print(f"\n📊 FINAL ASSESSMENT")
        print(f"Success rate: {success_rate:.1f}%")
        
        if validation_results['identical_assets_errors']:
            print("🚨 CRITICAL ISSUES FOUND - Trade logic needs fixing!")
            return False
        elif success_rate >= 90:
            print("✅ Trade logic appears to be working correctly!")
            return True
        else:
            print("⚠️  Some issues found but no critical errors")
            return True
            
    except Exception as e:
        print(f"❌ Error during validation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_trade_logic_validation()
    if not success:
        print("\n💥 Trade logic validation failed!")
        sys.exit(1)
    else:
        print("\n🎉 Trade logic validation passed!")