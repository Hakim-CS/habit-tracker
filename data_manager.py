import pandas as pd
import os
from datetime import datetime, timedelta

class HabitManager:
    def __init__(self):
        self.habits_file = "habits.csv"
        self.tracking_file = "tracking.csv"
        self.initialize_files()

    def initialize_files(self):
        if not os.path.exists(self.habits_file):
            pd.DataFrame(columns=['habit_id', 'name', 'description', 'created_date']).to_csv(self.habits_file, index=False)
        if not os.path.exists(self.tracking_file):
            pd.DataFrame(columns=['habit_id', 'date', 'completed']).to_csv(self.tracking_file, index=False)

    def add_habit(self, name, description):
        habits = pd.read_csv(self.habits_file)
        habit_id = len(habits) + 1
        new_habit = pd.DataFrame({
            'habit_id': [habit_id],
            'name': [name],
            'description': [description],
            'created_date': [datetime.now().strftime('%Y-%m-%d')]
        })
        habits = pd.concat([habits, new_habit], ignore_index=True)
        habits.to_csv(self.habits_file, index=False)
        return habit_id

    def get_habits(self):
        return pd.read_csv(self.habits_file)

    def track_habit(self, habit_id, date, completed):
        tracking = pd.read_csv(self.tracking_file)
        new_entry = pd.DataFrame({
            'habit_id': [habit_id],
            'date': [date],
            'completed': [completed]
        })
        # Remove existing entry for the same habit and date if exists
        tracking = tracking[~((tracking['habit_id'] == habit_id) & (tracking['date'] == date))]
        tracking = pd.concat([tracking, new_entry], ignore_index=True)
        tracking.to_csv(self.tracking_file, index=False)

    def get_tracking_data(self, habit_id=None):
        tracking = pd.read_csv(self.tracking_file)
        if habit_id:
            return tracking[tracking['habit_id'] == habit_id]
        return tracking

    def get_streak(self, habit_id):
        tracking = self.get_tracking_data(habit_id)
        if tracking.empty:
            return 0
        
        tracking = tracking[tracking['completed'] == True]
        if tracking.empty:
            return 0

        tracking['date'] = pd.to_datetime(tracking['date'])
        tracking = tracking.sort_values('date')
        
        current_streak = 0
        max_streak = 0
        prev_date = None

        for date in tracking['date']:
            if prev_date is None or (date - prev_date).days == 1:
                current_streak += 1
            else:
                current_streak = 1
            max_streak = max(max_streak, current_streak)
            prev_date = date

        return max_streak

    def get_completion_rate(self, habit_id):
        tracking = self.get_tracking_data(habit_id)
        if tracking.empty:
            return 0
        return (tracking['completed'] == True).mean() * 100
