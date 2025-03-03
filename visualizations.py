import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

def create_streak_chart(tracking_data, habit_name):
    fig = go.Figure()
    
    tracking_data['date'] = pd.to_datetime(tracking_data['date'])
    tracking_data = tracking_data.sort_values('date')
    
    fig.add_trace(go.Scatter(
        x=tracking_data['date'],
        y=tracking_data['completed'].astype(int),
        mode='lines+markers',
        name='Completed',
        line=dict(color='#FF4B4B'),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title=f'Streak Timeline for {habit_name}',
        xaxis_title='Date',
        yaxis_title='Completed',
        yaxis=dict(tickmode='array', tickvals=[0, 1], ticktext=['No', 'Yes']),
        showlegend=False,
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig

def create_completion_heatmap(tracking_data, habit_name):
    tracking_data['date'] = pd.to_datetime(tracking_data['date'])
    tracking_data['weekday'] = tracking_data['date'].dt.strftime('%A')
    tracking_data['week'] = tracking_data['date'].dt.strftime('%V')
    
    pivot_table = tracking_data.pivot_table(
        values='completed',
        index='weekday',
        columns='week',
        aggfunc='sum'
    )
    
    fig = px.imshow(
        pivot_table,
        color_continuous_scale=['#FFE5E5', '#FF4B4B'],
        title=f'Completion Heatmap for {habit_name}'
    )
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig

def create_progress_chart(completion_rate):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=completion_rate,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#FF4B4B"},
            'steps': [
                {'range': [0, 33], 'color': "#FFE5E5"},
                {'range': [33, 66], 'color': "#FFBFBF"},
                {'range': [66, 100], 'color': "#FF9999"}
            ]
        }
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    return fig
