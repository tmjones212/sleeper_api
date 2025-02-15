import csv
from datetime import datetime, timedelta
from typing import Dict, Tuple

class SeasonService:
    def __init__(self):
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
        with open(r'data\2024 Game Dates.csv', 'r') as csvfile:
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