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

    if 'value' in tracking_data.columns and not tracking_data['value'].isna().all():
        fig.add_trace(go.Scatter(
            x=tracking_data['date'],
            y=tracking_data['value'],
            mode='lines+markers',
            name='Value',
            line=dict(color='#4B4BFF'),
            marker=dict(size=8),
            yaxis='y2'
        ))

        fig.update_layout(
            yaxis2=dict(
                title='Value',
                overlaying='y',
                side='right'
            )
        )

    fig.update_layout(
        title=f'Progress Timeline for {habit_name}',
        xaxis_title='Date',
        yaxis_title='Completed',
        yaxis=dict(tickmode='array', tickvals=[0, 1], ticktext=['No', 'Yes']),
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
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

def create_comparative_analysis(tracking_data, habits_data):
    """Create a comparative analysis chart for multiple habits"""
    if tracking_data.empty or habits_data.empty:
        return None

    # Merge tracking data with habit information
    analysis_data = pd.merge(
        tracking_data,
        habits_data[['habit_id', 'name', 'priority']],
        on='habit_id'
    )

    # Calculate completion rates by priority
    completion_by_priority = analysis_data.groupby(
        ['name', 'priority']
    )['completed'].mean() * 100

    fig = go.Figure()

    # Add bars for each habit
    for name in completion_by_priority.index.get_level_values('name').unique():
        habit_data = completion_by_priority[name]
        fig.add_trace(go.Bar(
            name=name,
            x=[name],
            y=[habit_data],
            text=[f"{habit_data:.1f}%"],
            textposition='auto',
        ))

    fig.update_layout(
        title='Habit Comparison',
        yaxis_title='Completion Rate (%)',
        showlegend=True,
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    return fig

def create_priority_distribution(habits_data):
    """Create a pie chart showing the distribution of habit priorities"""
    priority_counts = habits_data['priority'].value_counts()

    fig = go.Figure(data=[go.Pie(
        labels=priority_counts.index,
        values=priority_counts.values,
        hole=.3
    )])

    fig.update_layout(
        title='Habits by Priority Level',
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    return fig