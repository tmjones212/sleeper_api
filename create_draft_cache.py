#!/usr/bin/env python3
"""
Create a draft cache JSON file with all draft data.
"""
import os
import sys
import json
sys.path.append('src')
from client import SleeperAPI

def create_draft_cache():
    """Generate draft cache JSON file"""
    client = SleeperAPI()
    
    # Your league IDs
    league_ids = [
        "1181025001438806016",  # 2025
        "1048308938824937472",  # 2024
        "916445745966915584",   # 2023
        "839251409999347712"    # 2022
    ]
    
    # Start with the most recent league
    main_league_id = league_ids[0]
    
    print(f"Getting draft data for league {main_league_id} and historical leagues...")
    
    # Get the league and follow the chain to collect all drafts
    league = client.league_service.get_league(main_league_id, fetch_all=True)
    
    draft_data = {
        'drafts_by_year': {},
        'available_years': [],
        'current_year': None
    }
    
    # Collect all league IDs in the chain
    all_league_ids = [main_league_id]
    current_league = league
    
    # Follow the previous_league_id chain
    while current_league and hasattr(current_league, 'previous_league_id') and current_league.previous_league_id:
        previous_id = current_league.previous_league_id
        if previous_id not in all_league_ids:
            all_league_ids.append(previous_id)
            try:
                current_league = client.league_service.get_league(previous_id, fetch_all=True)
            except:
                break
        else:
            break
    
    print(f"Found {len(all_league_ids)} leagues in chain: {all_league_ids}")
    
    # Get drafts from each league
    for league_id in all_league_ids:
        try:
            print(f"Processing drafts for league {league_id}...")
            
            # Get league info to determine year
            try:
                league_info = client.league_service.get_league(league_id, fetch_all=True)
                draft_year = int(league_info.season) if hasattr(league_info, 'season') else 2024
            except:
                # Fallback based on known league IDs
                year_mapping = {
                    "1181025001438806016": 2025,
                    "1048308938824937472": 2024,
                    "916445745966915584": 2023,
                    "839251409999347712": 2022
                }
                draft_year = year_mapping.get(league_id, 2024)
            
            drafts = client.draft_service.get_league_drafts(league_id)
            
            if drafts:
                year_drafts = []
                
                for draft in drafts:
                    draft_id = draft['draft_id']
                    print(f"  Processing draft {draft_id} for year {draft_year}...")
                    
                    # Get enhanced draft picks
                    picks = client.draft_service.get_draft_picks(draft_id)
                    
                    # Enhance picks with image URLs and traded status
                    enhanced_picks = []
                    for pick in picks:
                        enhanced_pick = {
                            'round': pick['round'],
                            'pick_in_round': pick['pick_in_round'],
                            'overall_pick': pick['overall_pick'],
                            'team': pick['team'],
                            'original_owner': pick['original_owner'],
                            'player_name': pick['player_name'],
                            'player_id': pick['player_id'],
                            'position': pick['position'],
                            'ktc_value': pick.get('ktc_value', 0),
                            'image_url': pick.get('image_url') or (
                                f"https://sleepercdn.com/content/nfl/players/thumb/{pick['player_id']}.jpg" 
                                if pick['player_id'] else None
                            ),
                            'was_traded': pick['team'] != pick['original_owner']
                        }
                        enhanced_picks.append(enhanced_pick)
                    
                    draft_info = {
                        'draft_id': draft_id,
                        'year': draft_year,
                        'type': draft.get('type', 'snake'),
                        'rounds': draft.get('settings', {}).get('rounds', 12),
                        'picks': enhanced_picks,
                        'stats': {
                            'total_picks': len(enhanced_picks),
                            'traded_picks': len([p for p in enhanced_picks if p['was_traded']]),
                            'total_rounds': max([p['round'] for p in enhanced_picks]) if enhanced_picks else 0
                        }
                    }
                    
                    year_drafts.append(draft_info)
                
                if year_drafts:
                    draft_data['drafts_by_year'][str(draft_year)] = year_drafts
                    draft_data['available_years'].append(draft_year)
                    
        except Exception as e:
            print(f"Error processing league {league_id}: {e}")
    
    # Set current year to the most recent
    if draft_data['available_years']:
        draft_data['available_years'].sort(reverse=True)
        draft_data['current_year'] = str(draft_data['available_years'][0])
    
    # Save to cache file
    cache_file = "data/draft_cache.json"
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(draft_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Draft cache saved to {cache_file}")
    print(f"Available years: {draft_data['available_years']}")
    print(f"Current year: {draft_data['current_year']}")
    
    # Print summary of what was cached
    for year, year_drafts in draft_data['drafts_by_year'].items():
        for draft in year_drafts:
            total_picks = len(draft['picks'])
            traded_picks = len([p for p in draft['picks'] if p['was_traded']])
            print(f"  {year}: {total_picks} picks ({traded_picks} traded)")
    
    return cache_file

if __name__ == "__main__":
    create_draft_cache()