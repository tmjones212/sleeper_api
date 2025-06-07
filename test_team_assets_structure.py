#!/usr/bin/env python3
"""
Test the team_assets structure to verify proper trade display
"""
import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from client import SleeperAPI

def test_team_assets_structure():
    """Test that team_assets structure shows proper trade data"""
    print("🔧 Testing Team Assets Structure")
    print("=" * 60)
    
    try:
        # Initialize API
        league_id = "1048308938824937472"
        api = SleeperAPI(league_id)
        
        # Get trades with new structure
        trades = api.transaction_service.get_trades(league_id)
        
        # Find Jerry Jeudy trade
        jeudy_trade = None
        for trade in trades:
            if '2024-01-24' in trade.get('date', ''):
                # Check if Jerry Jeudy is involved
                all_players = (trade.get('received', {}).get('players', []) + 
                              trade.get('given', {}).get('players', []))
                for player in all_players:
                    if 'JERRY JEUDY' in player.get('player', '').upper():
                        jeudy_trade = trade
                        break
                if jeudy_trade:
                    break
        
        if not jeudy_trade:
            print("❌ Jerry Jeudy trade not found")
            return False
        
        print("📋 JERRY JEUDY TRADE ANALYSIS")
        print(f"Date: {jeudy_trade.get('date')}")
        
        # Check if team_assets structure exists
        if 'team_assets' in jeudy_trade:
            print("\n✅ Found team_assets structure:")
            team_assets = jeudy_trade['team_assets']
            
            for team_name, assets in team_assets.items():
                print(f"\n📊 {team_name}:")
                
                print("  RECEIVES:")
                for asset in assets.get('receives', []):
                    if asset.get('type') == 'draft_pick':
                        print(f"    📋 {asset['round']} round {asset['season']} (from {asset.get('from_team', 'Unknown')})")
                    else:
                        print(f"    🏈 {asset['player']} (from {asset.get('from_team', 'Unknown')})")
                
                print("  GIVES:")
                for asset in assets.get('gives', []):
                    if asset.get('type') == 'draft_pick':
                        print(f"    📋 {asset['round']} round {asset['season']} (to {asset.get('to_team', 'Unknown')})")
                    else:
                        print(f"    🏈 {asset['player']} (to {asset.get('to_team', 'Unknown')})")
            
            # Verify the trade is correct
            tmjones_data = team_assets.get('tmjones212', {})
            emanuel_data = team_assets.get('emanueljd3', {})
            
            print(f"\n🔍 VERIFICATION:")
            
            # Check tmjones212 receives Jerry Jeudy
            tmjones_receives_jeudy = any(
                asset.get('player') == 'JERRY JEUDY' 
                for asset in tmjones_data.get('receives', [])
            )
            print(f"tmjones212 receives Jerry Jeudy: {'✅' if tmjones_receives_jeudy else '❌'}")
            
            # Check emanueljd3 receives 3rd round pick
            emanuel_receives_pick = any(
                asset.get('round') == 3 and asset.get('season') == '2024'
                for asset in emanuel_data.get('receives', [])
            )
            print(f"emanueljd3 receives 2024 3rd round pick: {'✅' if emanuel_receives_pick else '❌'}")
            
            # Check emanueljd3 gives Jerry Jeudy
            emanuel_gives_jeudy = any(
                asset.get('player') == 'JERRY JEUDY'
                for asset in emanuel_data.get('gives', [])
            )
            print(f"emanueljd3 gives Jerry Jeudy: {'✅' if emanuel_gives_jeudy else '❌'}")
            
            # Check tmjones212 gives 3rd round pick (should be in emanuel's receives)
            tmjones_gives_pick = any(
                asset.get('round') == 3 and asset.get('season') == '2024' and asset.get('from_team') == 'tmjones212'
                for asset in emanuel_data.get('receives', [])
            )
            print(f"tmjones212 gives 2024 3rd round pick: {'✅' if tmjones_gives_pick else '❌'}")
            
            all_correct = tmjones_receives_jeudy and emanuel_receives_pick and emanuel_gives_jeudy and tmjones_gives_pick
            
            if all_correct:
                print(f"\n🎉 TEAM ASSETS STRUCTURE IS CORRECT!")
                print("The visualization should now show proper trade details!")
                return True
            else:
                print(f"\n❌ TEAM ASSETS STRUCTURE HAS ISSUES")
                return False
        
        else:
            print("❌ team_assets structure not found in trade data")
            print("This means the trade processing isn't using the new structure")
            return False
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_team_assets_structure()
    if success:
        print("\n✅ Team assets structure test passed!")
    else:
        print("\n❌ Team assets structure test failed!")
        sys.exit(1)