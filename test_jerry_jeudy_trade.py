#!/usr/bin/env python3
"""
Test the Jerry Jeudy trade specifically to verify correct processing
"""
import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from client import SleeperAPI

def test_jerry_jeudy_trade():
    """Test the specific Jerry Jeudy trade mentioned by the user"""
    print("🎯 Testing Jerry Jeudy Trade")
    print("=" * 50)
    
    try:
        # Initialize API
        league_id = "1048308938824937472"
        api = SleeperAPI(league_id)
        
        # Get trades
        trades = api.transaction_service.get_trades(league_id)
        
        # Find Jerry Jeudy trades on 2024-01-24
        jeudy_trades = []
        for trade in trades:
            trade_date = trade.get('date', '')
            if '2024-01-24' in trade_date:
                # Check if Jerry Jeudy is involved
                all_players = (trade.get('received', {}).get('players', []) + 
                              trade.get('given', {}).get('players', []))
                for player in all_players:
                    if 'JERRY JEUDY' in player.get('player', '').upper():
                        jeudy_trades.append(trade)
                        break
        
        if not jeudy_trades:
            print("❌ No Jerry Jeudy trades found on 2024-01-24")
            return False
        
        print(f"Found {len(jeudy_trades)} Jerry Jeudy trade(s) on 2024-01-24:")
        
        for i, trade in enumerate(jeudy_trades):
            print(f"\n📋 Trade #{i+1}: {trade.get('date')}")
            
            print("\n🔽 RECEIVED ASSETS:")
            received_players = trade.get('received', {}).get('players', [])
            received_picks = trade.get('received', {}).get('draft_picks', [])
            
            for player in received_players:
                from_info = f" (from {player.get('from_team', 'Unknown')})" if player.get('from_team') else ""
                print(f"  • {player['team']}: {player['player']}{from_info}")
            
            for pick in received_picks:
                from_info = f" (from {pick.get('from_team', 'Unknown')})" if pick.get('from_team') else ""
                print(f"  • {pick.get('to_team', 'Unknown')}: {pick['round']} round {pick['season']} pick{from_info}")
            
            print("\n🔼 GIVEN ASSETS:")
            given_players = trade.get('given', {}).get('players', [])
            
            for player in given_players:
                to_info = f" (to {player.get('to_team', 'Unknown')})" if player.get('to_team') else ""
                print(f"  • {player['team']}: {player['player']}{to_info}")
            
            # Expected result based on user description:
            # tmjones212 got jeudy and traded away the 2024 round 3 pick
            # emanueljd3 got the 2024 round 3 pick and gave away jerry jeudy
            
            print(f"\n✅ EXPECTED vs ACTUAL:")
            print(f"Expected: tmjones212 receives Jerry Jeudy, gives 2024 Round 3 pick")
            print(f"Expected: emanueljd3 receives 2024 Round 3 pick, gives Jerry Jeudy")
            
            # Check if this matches
            tmjones_gets_jeudy = False
            tmjones_gives_pick = False
            emanuel_gets_pick = False
            emanuel_gives_jeudy = False
            
            for player in received_players:
                if 'tmjones212' in player['team'] and 'JERRY JEUDY' in player['player'].upper():
                    tmjones_gets_jeudy = True
                    print(f"✅ tmjones212 receives Jerry Jeudy: CORRECT")
            
            for pick in received_picks:
                if 'emanueljd3' in pick.get('to_team', '') and pick['round'] == 3 and pick['season'] == '2024':
                    emanuel_gets_pick = True
                    print(f"✅ emanueljd3 receives 2024 Round 3 pick: CORRECT")
            
            for player in given_players:
                if 'emanueljd3' in player['team'] and 'JERRY JEUDY' in player['player'].upper():
                    emanuel_gives_jeudy = True
                    print(f"✅ emanueljd3 gives Jerry Jeudy: CORRECT")
            
            # Check for tmjones giving pick (this might be in the draft picks structure)
            for pick in received_picks:
                if 'tmjones212' in pick.get('from_team', '') and pick['round'] == 3 and pick['season'] == '2024':
                    tmjones_gives_pick = True
                    print(f"✅ tmjones212 gives 2024 Round 3 pick: CORRECT")
            
            # Summary
            all_correct = tmjones_gets_jeudy and tmjones_gives_pick and emanuel_gets_pick and emanuel_gives_jeudy
            
            if all_correct:
                print(f"\n🎉 TRADE PROCESSING IS CORRECT!")
                return True
            else:
                print(f"\n❌ TRADE PROCESSING HAS ISSUES:")
                print(f"   tmjones212 gets Jeudy: {tmjones_gets_jeudy}")
                print(f"   tmjones212 gives Pick: {tmjones_gives_pick}")
                print(f"   emanueljd3 gets Pick: {emanuel_gets_pick}")
                print(f"   emanueljd3 gives Jeudy: {emanuel_gives_jeudy}")
                return False
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_jerry_jeudy_trade()
    if success:
        print("\n✅ Jerry Jeudy trade test passed!")
    else:
        print("\n❌ Jerry Jeudy trade test failed!")
        sys.exit(1)