#!/usr/bin/env python3
"""Create a fixed version of the transaction service."""

import sys
sys.path.append('src')

def create_fix():
    # Read the original file
    with open('src/transaction_service.py', 'r') as f:
        content = f.read()
    
    # The issue is in _get_historical_team_name - it needs better handling
    # when the league chain can't be followed properly
    
    # Find the _get_draft_pick_details method
    fix_code = '''
    def _get_draft_pick_details(self, pick_data: Dict[str, Any], roster_to_team: Dict[int, str], league_id: str) -> Optional[Dict[str, Any]]:
        """Get actual draft pick details (pick number, player) if the draft has happened."""
        try:
            season = pick_data['season']
            round_num = pick_data['round']
            
            # For future drafts (2025+), we need to look in the appropriate league
            # Use hardcoded league mapping as fallback
            league_mapping = {
                '2025': '1181025001438806016',
                '2024': '1048308938824937472',
                '2023': '916445745966915584',
                '2022': '839251409999347712'
            }
            
            # Try to find the league for this season
            target_league_id = self._find_league_for_season(league_id, season)
            if not target_league_id and str(season) in league_mapping:
                target_league_id = league_mapping[str(season)]
            
            if not target_league_id:
                return None
            
            # Get draft data for that season
            from draft_service import DraftService
            draft_service = DraftService(self.client)
            
            try:
                drafts = draft_service.get_league_drafts(target_league_id)
                if not drafts:
                    return None
                
                # Get the main draft (usually first one)
                draft_id = drafts[0]['draft_id']
                picks = draft_service.get_draft_picks(draft_id)
                
                # Get the original roster ID
                original_roster_id = pick_data.get('roster_id', pick_data['previous_owner_id'])
                
                # IMPORTANT: For cross-league trades, we need to map the roster ID
                # to the correct team name in the TARGET league, not the source league
                
                # Get roster mapping for the TARGET league (where the draft happened)
                target_rosters = self.client.league_service.get_league_rosters(target_league_id)
                target_users = self.client.league_service.get_league_users(target_league_id)
                target_roster_to_team = {}
                for roster in target_rosters:
                    team = next((u for u in target_users if u.user_id == roster.owner_id), None)
                    if team:
                        target_roster_to_team[roster.roster_id] = team.display_name
                
                # Get the team name - but handle the case where roster IDs don't match
                # between leagues (e.g., emanueljd3 might be roster 7 in one league but
                # have a different roster ID in another)
                original_owner_name = None
                
                # First try direct roster mapping in target league
                if original_roster_id in target_roster_to_team:
                    original_owner_name = target_roster_to_team[original_roster_id]
                
                # If that doesn't work, we need to be smarter
                # The roster_id represents the draft slot, so we need to find who had
                # that draft slot in the target league
                if not original_owner_name or original_owner_name.startswith("Team "):
                    # Get draft order to map positions to teams
                    draft_order = drafts[0].get('processed_draft_order', {})
                    
                    # In the draft order, positions are 1-based
                    # Roster IDs typically match draft positions
                    if str(original_roster_id) in draft_order:
                        original_owner_name = draft_order[str(original_roster_id)]
                    elif original_roster_id in draft_order:
                        original_owner_name = draft_order[original_roster_id]
                
                # If still not found, try to use historical lookup as last resort
                if not original_owner_name:
                    original_owner_name = self._get_historical_team_name(
                        original_roster_id, season, league_id, roster_to_team
                    )
                
                # Now try to match the pick
                for draft_pick in picks:
                    if (draft_pick['round'] == round_num and 
                        draft_pick['original_owner'] == original_owner_name):
                        return {
                            'pick_number': draft_pick['overall_pick'],
                            'player_name': draft_pick['player_name'],
                            'player_id': draft_pick['player_id'],
                            'position': draft_pick['position'],
                            'image_url': draft_pick.get('image_url')
                        }
                
            except Exception as e:
                print(f"Could not get draft details for {season} round {round_num}: {e}")
                return None
                
        except Exception as e:
            print(f"Error getting draft pick details: {e}")
            return None
        
        return None
'''
    
    print("Fix has been prepared. The issue is that when processing historical trades,")
    print("the roster IDs don't necessarily match between leagues.")
    print("")
    print("The fix involves:")
    print("1. Using the draft order from the target league to map roster IDs to team names")
    print("2. Handling the case where emanueljd3 is roster 7 in the 2023 league")
    print("   but has draft position 10 in the 2025 draft")
    print("")
    print("To apply this fix, the _get_draft_pick_details method in transaction_service.py")
    print("needs to be updated to better handle cross-league roster ID mapping.")

if __name__ == "__main__":
    create_fix()