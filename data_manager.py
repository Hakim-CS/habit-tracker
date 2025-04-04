import pandas as pd
import os
from datetime import datetime, timedelta
import json

class HabitManager: 
    def __init__(self):
        self.habits_file = "habits.csv"
        self.tracking_file = "tracking.csv"
        self.initialize_files()
        self.migrate_existing_data()

    def initialize_files(self):
        columns = [
            'habit_id', 'name', 'description', 'created_date',
            'priority', 'goal_type', 'goal_value', 'reminder_time'
        ]
        if not os.path.exists(self.habits_file):
            pd.DataFrame(columns=columns).to_csv(self.habits_file, index=False)
        if not os.path.exists(self.tracking_file):
            pd.DataFrame(columns=['habit_id', 'date', 'completed', 'value']).to_csv(self.tracking_file, index=False)

    def migrate_existing_data(self):
        """Add new columns with default values if they don't exist"""
        try:
            habits = pd.read_csv(self.habits_file)
            tracking = pd.read_csv(self.tracking_file)

            # Add new columns to habits if they don't exist
            if 'priority' not in habits.columns:
                habits['priority'] = 'medium'
            if 'goal_type' not in habits.columns:
                habits['goal_type'] = 'completion'
            if 'goal_value' not in habits.columns:
                habits['goal_value'] = 100
            if 'reminder_time' not in habits.columns:
                habits['reminder_time'] = None

            # Add value column to tracking if it doesn't exist
            if 'value' not in tracking.columns:
                tracking['value'] = None

            habits.to_csv(self.habits_file, index=False)
            tracking.to_csv(self.tracking_file, index=False)
        except Exception as e:
            print(f"Migration error: {str(e)}")

    def add_habit(self, name, description, priority='medium', goal_type='completion', goal_value=100, reminder_time=None):
        habits = pd.read_csv(self.habits_file)
        habit_id = len(habits) + 1
        new_habit = pd.DataFrame({
            'habit_id': [habit_id],
            'name': [name],
            'description': [description],
            'created_date': [datetime.now().strftime('%Y-%m-%d')],
            'priority': [priority],
            'goal_type': [goal_type],
            'goal_value': [goal_value],
            'reminder_time': [reminder_time]
        })
        habits = pd.concat([habits, new_habit], ignore_index=True)
        habits.to_csv(self.habits_file, index=False)
        return habit_id

    def update_habit(self, habit_id, **kwargs):
        habits = pd.read_csv(self.habits_file)
        for key, value in kwargs.items():
            habits.loc[habits['habit_id'] == habit_id, key] = value
        habits.to_csv(self.habits_file, index=False)

    def export_data(self, habit_id=None):
        habits = pd.read_csv(self.habits_file)
        tracking = pd.read_csv(self.tracking_file)

        if habit_id:
            habits = habits[habits['habit_id'] == habit_id]
            tracking = tracking[tracking['habit_id'] == habit_id]

        export_data = {
            'habits': habits.to_dict('records'),
            'tracking': tracking.to_dict('records'),
            'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        return json.dumps(export_data, indent=2)

    def import_data(self, json_data):
        try:
            data = json.loads(json_data)
            habits_df = pd.DataFrame(data['habits'])
            tracking_df = pd.DataFrame(data['tracking'])

            # Ensure all required columns exist
            required_habit_columns = [
                'habit_id', 'name', 'description', 'created_date',
                'priority', 'goal_type', 'goal_value', 'reminder_time'
            ]
            required_tracking_columns = ['habit_id', 'date', 'completed', 'value']

            for col in required_habit_columns:
                if col not in habits_df.columns:
                    habits_df[col] = None

            for col in required_tracking_columns:
                if col not in tracking_df.columns:
                    tracking_df[col] = None

            habits_df.to_csv(self.habits_file, index=False)
            tracking_df.to_csv(self.tracking_file, index=False)
        except Exception as e:
            raise ValueError(f"Error importing data: {str(e)}")

    def get_habits(self):
        habits = pd.read_csv(self.habits_file)
        # Ensure required columns exist with default values
        if 'priority' not in habits.columns:
            habits['priority'] = 'medium'
        if 'goal_type' not in habits.columns:
            habits['goal_type'] = 'completion'
        if 'goal_value' not in habits.columns:
            habits['goal_value'] = 100
        if 'reminder_time' not in habits.columns:
            habits['reminder_time'] = None
        return habits

    def track_habit(self, habit_id, date, completed, value=None):
        tracking = pd.read_csv(self.tracking_file)
        new_entry = pd.DataFrame({
            'habit_id': [habit_id],
            'date': [date],
            'completed': [completed],
            'value': [value]
        })
        tracking = tracking[~((tracking['habit_id'] == habit_id) & (tracking['date'] == date))]
        tracking = pd.concat([tracking, new_entry], ignore_index=True)
        tracking.to_csv(self.tracking_file, index=False)

    def get_tracking_data(self, habit_id=None):
        tracking = pd.read_csv(self.tracking_file)
        if 'value' not in tracking.columns:
            tracking['value'] = None
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

    def get_goal_progress(self, habit_id):
        habit = self.get_habits()
        habit = habit[habit['habit_id'] == habit_id].iloc[0]
        tracking = self.get_tracking_data(habit_id)

        if habit['goal_type'] == 'completion':
            if tracking.empty:
                return 0
            return (tracking['completed'] == True).mean() * 100
        else:
            if tracking.empty:
                return 0
            return (tracking['value'].sum() / habit['goal_value']) * 100
