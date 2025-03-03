from datetime import datetime, timedelta

def get_date_range(days=30):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date

def format_date(date):
    return date.strftime('%Y-%m-%d')

def calculate_completion_stats(tracking_data):
    if tracking_data.empty:
        return {
            'total_days': 0,
            'completed_days': 0,
            'completion_rate': 0
        }
    
    total_days = len(tracking_data)
    completed_days = len(tracking_data[tracking_data['completed'] == True])
    completion_rate = (completed_days / total_days) * 100 if total_days > 0 else 0
    
    return {
        'total_days': total_days,
        'completed_days': completed_days,
        'completion_rate': round(completion_rate, 1)
    }
