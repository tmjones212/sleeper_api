import csv
import os
from datetime import datetime, timedelta
from typing import Dict, Tuple

class WeekService:
    def __init__(self):
        # Define the base directory for data files
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(os.path.dirname(self.base_dir), 'data')
        self.week_ranges = self._load_week_ranges()

    def get_current_week(self) -> int:
        current_date = datetime.now().date()

        for week, (start_date, end_date) in sorted(self.week_ranges.items()):
            if current_date <= end_date:
                return week

        # If we're past the last week, return the last week number
        return max(self.week_ranges.keys())
    
    def get_current_season_year(self) -> int:
        current_date = datetime.now().date()
        
        for week, (start_date, end_date) in self.week_ranges.items():
            if current_date <= end_date:
                return start_date.year
        
        # If we're past the last game, return the year of the last game
        return max(end_date.year for _, end_date in self.week_ranges.values())

    def _load_week_ranges(self) -> Dict[int, Tuple[datetime.date, datetime.date]]:
        week_ranges = {}
        
        # Use absolute path with os.path.join
        file_path = os.path.join(self.data_dir, '2024 Game Dates.csv')
        
        try:
            with open(file_path, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    week = int(row['WeekNum'])
                    date = datetime.strptime(row['ScheduleDate'], '%Y-%m-%d %H:%M:%S').date()
                    
                    if week not in week_ranges:
                        week_ranges[week] = [date, date]  # [start_date, end_date]
                    else:
                        week_ranges[week][0] = min(week_ranges[week][0], date)
                        week_ranges[week][1] = max(week_ranges[week][1], date)

            # Adjust the start and end dates for each week
            sorted_weeks = sorted(week_ranges.keys())
            for i in range(len(sorted_weeks)):
                current_week = sorted_weeks[i]
                
                # Set start date (except for week 1)
                if i > 0:
                    previous_week = sorted_weeks[i-1]
                    week_ranges[current_week][0] = week_ranges[previous_week][1] + timedelta(days=1)
                    
            return week_ranges
            
        except FileNotFoundError:
            print(f"ERROR: Could not find file at {file_path}")
            # Provide empty data
            return {} 