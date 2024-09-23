import requests

from exceptions import SleeperAPIException
from models import PlayerProp, Transaction


class DraftKingsAPI:
    BASE_URL = "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusnj/v1"
    _subcategories = None  # Class variable to store subcategories
    PLAYER_STATS_CATEGORY_ID = 782  # Fixed category ID for player stats

    @staticmethod
    def get_nfl_player_props(week, prop_type):
        url = f"{DraftKingsAPI.BASE_URL}/leagues/88808/categories/1001/subcategories/9523"
        
        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "origin": "https://sportsbook.draftkings.com",
            "referer": "https://sportsbook.draftkings.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            player_props = DraftKingsAPI.extract_player_props(data, prop_type)
            
            return player_props
        except requests.RequestException as e:
            raise SleeperAPIException(f"Error fetching DraftKings data: {str(e)}")

    @classmethod
    def get_nfl_player_props_2(cls, prop_type):
        subcategory_id = cls.get_subcategory_id(prop_type)
        if subcategory_id is None:
            raise ValueError(f"Prop type '{prop_type}' not found in subcategories")
        
        url = f"{cls.BASE_URL}/leagues/88808/categories/{cls.PLAYER_STATS_CATEGORY_ID}/subcategories/{subcategory_id}"
        
        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "origin": "https://sportsbook.draftkings.com",
            "referer": "https://sportsbook.draftkings.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            player_props = cls.extract_player_props(data, prop_type)
            
            return player_props
        except requests.RequestException as e:
            raise SleeperAPIException(f"Error fetching DraftKings data: {str(e)}")

    @staticmethod
    def extract_player_props(data, prop_type):
        player_props = []
        
        for selection in data.get('selections', []):
            player_name = selection.get('participants', [{}])[0].get('name', '')
            prop_value = float(selection.get('points', 0))
            over_line = selection.get('displayOdds', {}).get('american', '')
            
            # Find the corresponding Under selection
            under_selection = next((s for s in data.get('root', {}).get('selections', [])
                                    if s.get('participants', [{}])[0].get('name') == player_name
                                    and s.get('outcomeType') == 'Under'), {})
            under_line = under_selection.get('displayOdds', {}).get('american', '')
            
            # Team and opponent information is not available in this data structure
            # You might need to fetch this information from elsewhere or leave it blank
            team = ''
            opponent = ''
            
            player_prop = PlayerProp(
                player_name=player_name,
                team=team,
                opponent=opponent,
                prop_type=prop_type,
                prop_value=prop_value,
                over_line=over_line,
                under_line=under_line
            )
            player_props.append(player_prop)

        return player_props

    @staticmethod
    def get_all_subcategories():
        url = f"{DraftKingsAPI.BASE_URL}/leagues/88808/categories/1001/subcategories/9523"
        
        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "origin": "https://sportsbook.draftkings.com",
            "referer": "https://sportsbook.draftkings.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            subcategories = data.get('subcategories', [])
            
            return [
                {
                    'id': sub['id'],
                    'categoryId': sub['categoryId'],
                    'name': sub['name'],
                    'componentId': sub['componentId'],
                    'sortOrder': sub['sortOrder'],
                    'tags': sub.get('tags', [])
                }
                for sub in subcategories
            ]
        except requests.RequestException as e:
            raise SleeperAPIException(f"Error fetching DraftKings subcategories: {str(e)}")

    @classmethod
    def get_subcategory_id(cls, prop_type):
        if cls._subcategories is None:
            cls._subcategories = cls.get_all_subcategories()
        
        if isinstance(prop_type, int):
            # If the identifier is an integer, assume it's already an ID
            for subcategory in cls._subcategories:
                if subcategory['id'] == prop_type:
                    return subcategory['id']
        elif isinstance(prop_type, str):
            # If the identifier is a string, search by name
            for subcategory in cls._subcategories:
                if subcategory['name'].lower() == prop_type.lower():
                    return subcategory['id']
        
        return None  # Return None if subcategory not found

    @classmethod
    def get_all_subcategories(cls):
        if cls._subcategories is not None:
            return cls._subcategories

        url = f"{cls.BASE_URL}/leagues/88808/categories/1001/subcategories/9523"
        
        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "origin": "https://sportsbook.draftkings.com",
            "referer": "https://sportsbook.draftkings.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            cls._subcategories = [
                {
                    'id': sub['id'],
                    'categoryId': sub['categoryId'],
                    'name': sub['name'],
                    'componentId': sub['componentId'],
                    'sortOrder': sub['sortOrder'],
                    'tags': sub.get('tags', [])
                }
                for sub in data.get('subcategories', [])
            ]
            
            return cls._subcategories
        except requests.RequestException as e:
            raise SleeperAPIException(f"Error fetching DraftKings subcategories: {str(e)}")