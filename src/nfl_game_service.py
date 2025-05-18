from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
import requests
import zipfile
import io
import base64
import csv
import os
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class NflGame:
    schedule_date: datetime
    schedule_season: int
    schedule_week: Union[int, str]  # Can be either int or str
    team_home: str
    team_away: str
    team_favorite_id: str
    spread_favorite: float
    over_under_line: float
    stadium: str
    weather_temperature: float
    weather_wind_mph: float
    weather_humidity: float
    weather_detail: str
    score_home: int
    score_away: int
    game_id: Optional[str] = None
    game_status: Optional[str] = None
    game_quarter: Optional[int] = None
    game_clock: Optional[str] = None

class NflGameService:
    def __init__(self, kaggle_username: str, kaggle_api_key: str):
        """Initialize the NFL Game Service with Kaggle credentials."""
        if not kaggle_username or not kaggle_api_key:
            raise ValueError("Kaggle username and API key are required")
        self.kaggle_username = kaggle_username
        self.kaggle_api_key = kaggle_api_key
        self.base_url = "https://www.kaggle.com/api/v1"
        self.dataset_path = "tobycrabtree/nfl-scores-and-betting-data"
        self.data_dir = Path("data/nfl_games")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.csv_file = self.data_dir / "nfl_games.csv"

    def _get_csv_metadata(self) -> Optional[datetime]:
        """Get the last modified time of the CSV file if it exists."""
        if self.csv_file.exists():
            return datetime.fromtimestamp(self.csv_file.stat().st_mtime)
        return None

    def _get_latest_game_date(self) -> Optional[datetime]:
        """Get the latest schedule_date from the CSV file."""
        if not self.csv_file.exists():
            return None
        
        latest_date = None
        with open(self.csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    game_date = datetime.strptime(row['schedule_date'], '%m/%d/%Y')
                    if latest_date is None or game_date > latest_date:
                        latest_date = game_date
                except (ValueError, KeyError):
                    continue
        return latest_date

    def _needs_update(self) -> bool:
        """
        Check if the CSV file needs to be updated based on:
        1. If file doesn't exist
        2. If latest game date is after file's last modified time
        3. If 2025 game is missing
        """
        if not self.csv_file.exists():
            return True

        file_modified_time = self._get_csv_metadata()
        latest_game_date = self._get_latest_game_date()

        if not file_modified_time or not latest_game_date:
            return True

        # Check if 2025 game exists in the CSV
        has_2025_game = False
        try:
            with open(self.csv_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('schedule_season') == '2025':
                        has_2025_game = True
                        break
        except Exception as e:
            logger.error(f"Error checking for 2025 game: {e}")
            return True

        # If the latest game date is after the file's last modified time,
        # or if the 2025 game is missing, we need to update the file
        return latest_game_date > file_modified_time or not has_2025_game

    def _add_2025_record_if_needed(self, games: List[NflGame]) -> List[NflGame]:
        """Add the 2025 record if it doesn't exist in the games list."""
        # Check if we already have any 2025 games
        has_2025_games = any(game.schedule_season == 2025 for game in games)
        
        if not has_2025_games:
            logger.info("Adding 2025 record")
            future_game = NflGame(
                schedule_date=datetime.strptime('09/04/2025', '%m/%d/%Y'),
                schedule_season=2025,
                schedule_week=1,
                team_home='Philadelphia Eagles',
                team_away='Dallas Cowboys',
                team_favorite_id='PHI',
                spread_favorite=-7.0,
                over_under_line=46.5,
                stadium='Corinthians Arena',
                weather_temperature=0.0,
                weather_wind_mph=0.0,
                weather_humidity=0.0,
                weather_detail='',
                score_home=0,
                score_away=0
            )
            games.append(future_game)
        
        return games

    def get_nfl_games(self, season: Optional[int] = None) -> List[NflGame]:
        """
        Get NFL games data, optionally filtered by season.
        
        Args:
            season (int, optional): Filter games by season year
            
        Returns:
            List[NflGame]: List of NFL game objects
        """
        logger.info(f"Getting NFL games for season: {season}")
        
        # Check if we need to update the CSV file
        if self._needs_update():
            logger.info("CSV needs update, downloading fresh data")
            games = self._download_and_process_games()
            if not games:
                logger.error("No games downloaded from Kaggle")
                return []
            
            # Add 2025 record if needed before caching
            games = self._add_2025_record_if_needed(games)
            self._cache_games(games, self.csv_file)
        else:
            logger.info("Loading games from cache")
            games = self._load_games_from_cache(self.csv_file)
            if not games:
                logger.error("No games loaded from cache")
                return []
            
            # Add 2025 record if needed after loading from cache
            games = self._add_2025_record_if_needed(games)
            # Update cache with 2025 game if it was added
            if any(game.schedule_season == 2025 for game in games):
                self._cache_games(games, self.csv_file)
        
        # Filter by season if specified
        if season:
            logger.info(f"Filtering games for season {season}")
            games = [game for game in games if game.schedule_season == season]
        
        # Sort games by date in descending order
        games.sort(key=lambda x: x.schedule_date, reverse=True)
        logger.info(f"Returning {len(games)} games")
        return games

    def get_games_by_week(self, season: int, week: int) -> List[NflGame]:
        """
        Get NFL games for a specific season and week.
        
        Args:
            season (int): The season year
            week (int): The week number
            
        Returns:
            List[NflGame]: List of NFL game objects for the specified week
        """
        games = self.get_nfl_games(season)
        return [game for game in games if game.schedule_week == week]

    def get_team_games(self, team: str, season: Optional[int] = None) -> List[NflGame]:
        """
        Get all games for a specific team, optionally filtered by season.
        
        Args:
            team (str): Team abbreviation (e.g., 'SF', 'KC')
            season (int, optional): Filter by season year
            
        Returns:
            List[NflGame]: List of NFL game objects for the specified team
        """
        games = self.get_nfl_games(season)
        return [game for game in games 
                if game.team_home == team or game.team_away == team]

    def get_team_record(self, team: str, season: int) -> Dict[str, int]:
        """
        Get a team's win-loss record for a specific season.
        
        Args:
            team (str): Team abbreviation
            season (int): Season year
            
        Returns:
            Dict[str, int]: Dictionary with wins, losses, and ties
        """
        games = self.get_team_games(team, season)
        record = {'wins': 0, 'losses': 0, 'ties': 0}
        
        for game in games:
            if game.score_home == game.score_away:
                record['ties'] += 1
            elif (game.team_home == team and game.score_home > game.score_away) or \
                 (game.team_away == team and game.score_away > game.score_home):
                record['wins'] += 1
            else:
                record['losses'] += 1
                
        return record

    def _download_and_process_games(self) -> List[NflGame]:
        """Download and process NFL game data from Kaggle."""
        logger.info("Downloading games from Kaggle")
        client = requests.Session()
        file_name = "spreadspoke_scores.csv"

        def safe_float_convert(value: str) -> float:
            """Safely convert a string to float, handling empty or whitespace values."""
            if not value or value.strip() == '':
                return 0.0
            try:
                return float(value)
            except ValueError:
                return 0.0

        try:
            # Set up authentication
            auth_string = f"{self.kaggle_username}:{self.kaggle_api_key}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            client.headers.update({
                'Authorization': f'Basic {auth_b64}'
            })

            # Download the dataset
            response = client.get(f"{self.base_url}/datasets/download/{self.dataset_path}")
            response.raise_for_status()

            games = []
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                for file_info in zip_file.filelist:
                    if file_info.filename.endswith(file_name):
                        with zip_file.open(file_info) as csv_file:
                            # Decode bytes to text
                            csv_text = csv_file.read().decode('utf-8')
                            reader = csv.DictReader(io.StringIO(csv_text))
                            for row in reader:
                                try:
                                    # Handle schedule_week conversion
                                    try:
                                        schedule_week = int(row['schedule_week'])
                                    except ValueError:
                                        schedule_week = row['schedule_week']  # Keep as string if not numeric
                                    
                                    game = NflGame(
                                        schedule_date=datetime.strptime(row['schedule_date'], '%m/%d/%Y'),
                                        schedule_season=int(row['schedule_season']),
                                        schedule_week=schedule_week,
                                        team_home=row['team_home'],
                                        team_away=row['team_away'],
                                        team_favorite_id=row['team_favorite_id'],
                                        spread_favorite=safe_float_convert(row['spread_favorite']),
                                        over_under_line=safe_float_convert(row['over_under_line']),
                                        stadium=row['stadium'],
                                        weather_temperature=safe_float_convert(row['weather_temperature']),
                                        weather_wind_mph=safe_float_convert(row['weather_wind_mph']),
                                        weather_humidity=safe_float_convert(row['weather_humidity']),
                                        weather_detail=row['weather_detail'],
                                        score_home=int(row['score_home']) if row['score_home'] else 0,
                                        score_away=int(row['score_away']) if row['score_away'] else 0
                                    )
                                    games.append(game)
                                except Exception as e:
                                    logger.warning(f"Error processing row: {e}")
                                    continue

            logger.info(f"Successfully downloaded and processed {len(games)} games")
            return games
        except Exception as e:
            logger.error(f"Error downloading games: {e}")
            return []

    def _load_games_from_cache(self, cache_file: Path) -> List[NflGame]:
        """Load games from cache file."""
        logger.info(f"Loading games from cache file: {cache_file}")
        games = []
        try:
            with open(cache_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        game = NflGame(
                            schedule_date=datetime.strptime(row['schedule_date'], '%m/%d/%Y'),
                            schedule_season=int(row['schedule_season']),
                            schedule_week=row['schedule_week'],
                            team_home=row['team_home'],
                            team_away=row['team_away'],
                            team_favorite_id=row['team_favorite_id'],
                            spread_favorite=float(row['spread_favorite']) if row['spread_favorite'] else 0.0,
                            over_under_line=float(row['over_under_line']) if row['over_under_line'] else 0.0,
                            stadium=row['stadium'],
                            weather_temperature=float(row['weather_temperature']) if row['weather_temperature'] else 0.0,
                            weather_wind_mph=float(row['weather_wind_mph']) if row['weather_wind_mph'] else 0.0,
                            weather_humidity=float(row['weather_humidity']) if row['weather_humidity'] else 0.0,
                            weather_detail=row['weather_detail'],
                            score_home=int(row['score_home']) if row['score_home'] else 0,
                            score_away=int(row['score_away']) if row['score_away'] else 0
                        )
                        games.append(game)
                    except (ValueError, KeyError) as e:
                        logger.warning(f"Error processing row: {e}")
                        continue
            logger.info(f"Successfully loaded {len(games)} games from cache")
            return games
        except Exception as e:
            logger.error(f"Error loading games from cache: {e}")
            return []

    def _cache_games(self, games: List[NflGame], cache_file: Path):
        """Cache games to CSV file."""
        with open(cache_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=NflGame.__annotations__.keys())
            writer.writeheader()
            for game in games:
                writer.writerow({
                    'schedule_date': game.schedule_date.strftime('%m/%d/%Y'),
                    'schedule_season': game.schedule_season,
                    'schedule_week': game.schedule_week,
                    'team_home': game.team_home,
                    'team_away': game.team_away,
                    'team_favorite_id': game.team_favorite_id,
                    'spread_favorite': game.spread_favorite,
                    'over_under_line': game.over_under_line,
                    'stadium': game.stadium,
                    'weather_temperature': game.weather_temperature,
                    'weather_wind_mph': game.weather_wind_mph,
                    'weather_humidity': game.weather_humidity,
                    'weather_detail': game.weather_detail,
                    'score_home': game.score_home,
                    'score_away': game.score_away
                })

# Example usage:
if __name__ == "__main__":
    # Initialize the service with your Kaggle credentials
    nfl_service = NflGameService(
        kaggle_username="trentjones212",
        kaggle_api_key=os.getenv('kaggle_api_key')
    )

    all_games = nfl_service.get_nfl_games()
    # Get all games for the 2023 season
    games_2023 = nfl_service.get_nfl_games(2023)
    
    # Get games for a specific week
    week_1_games = nfl_service.get_games_by_week(2023, 1)
    
    # Get all games for a specific team
    sf_games = nfl_service.get_team_games("SF", 2023)
    
    # Get a team's record
    sf_record = nfl_service.get_team_record("SF", 2023)
    print(f"49ers 2023 Record: {sf_record['wins']}-{sf_record['losses']}-{sf_record['ties']}")