import streamlit as st
import pandas as pd
from datetime import datetime
# import json 
from data_manager import HabitManager 
from visualizations import create_streak_chart, create_completion_heatmap, create_progress_chart
from utils import get_date_range, format_date, calculate_completion_stats

# Initialize session state
if 'habit_manager' not in st.session_state:
    st.session_state.habit_manager = HabitManager()

# page configuration ...
st.set_page_config(
    page_title="Habit Tracker",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("📊 Habit Tracker")
st.markdown("""
    Track your daily habits and build better routines with interactive visualizations 
    and progress tracking.
""")

# Sidebar for adding new habits
with st.sidebar:
    st.header("Add New Habit")
    new_habit_name = st.text_input("Habit Name")
    new_habit_desc = st.text_area("Description")

    # Add priority and goal settings
    priority = st.selectbox("Priority Level", ["Low", "Medium", "High"], index=1)
    goal_type = st.selectbox("Goal Type", ["Completion Rate", "Numeric Value"])
    goal_value = st.number_input("Goal Value", min_value=1, value=100)
    reminder_time = st.time_input("Set Reminder Time (Optional)")

    if st.button("Add Habit"):
        if new_habit_name:
            st.session_state.habit_manager.add_habit(
                new_habit_name,
                new_habit_desc,
                priority=priority.lower(),
                goal_type='completion' if goal_type == "Completion Rate" else 'numeric',
                goal_value=goal_value,
                reminder_time=reminder_time.strftime("%H:%M") if reminder_time else None
            )
            st.success(f"Added new habit: {new_habit_name}")
        else:
            st.error("Please enter a habit name")

    # Data Export/Import Section
    st.markdown("---")
    st.header("Data Management")

    # Export Data
    if st.button("Export Data"):
        data = st.session_state.habit_manager.export_data()
        st.download_button(
            label="Download Habits Data",
            data=data,
            file_name=f"habits_export_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )

    # Import Data
    uploaded_file = st.file_uploader("Import Data", type=['json'])
    if uploaded_file is not None:
        try:
            json_data = uploaded_file.read().decode()
            st.session_state.habit_manager.import_data(json_data)
            st.success("Data imported successfully!")
        except Exception as e:
            st.error(f"Error importing data: {str(e)}")

    # About section
    st.markdown("---")
    st.header("About")
    st.markdown("""
        ### About the Developer
        👨‍💻 **Abdul Hakim Nazari**  
        Computer Engineering Student  
        Pamukkale University  
        📧 [hakim.nazari.tech@gmail.com](mailto:hakim.nazari.tech@gmail.com)

        ### About this Project
        This is a web-based habit tracker application built with Streamlit, 
        designed to help you build better routines through visualization 
        and progress tracking. Access it from any device with a web browser!

        #### Features:
        - 📊 Interactive visualizations
        - 🎯 Goal setting and tracking
        - 📱 Mobile-responsive design
        - 💾 Data export/import capability
        - ⭐ Priority-based habit management
    """)


# Main content
habits = st.session_state.habit_manager.get_habits()

if habits.empty:
    st.info("No habits added yet. Create your first habit using the sidebar!")
else:
    # Habit selection
    selected_habit = st.selectbox(
        "Select a habit to track",
        options=habits['habit_id'].tolist(),
        format_func=lambda x: f"{habits[habits['habit_id'] == x]['name'].iloc[0]} ({habits[habits['habit_id'] == x]['priority'].iloc[0].title()})"
    )

    # Get habit details
    habit_data = habits[habits['habit_id'] == selected_habit].iloc[0]
    habit_name = habit_data['name']

    # Create columns for layout
    col1, col2, col3 = st.columns(3)

    with col1:
        # Track today's habit
        st.subheader("Track Today")
        today = datetime.now().strftime('%Y-%m-%d')
        completed = st.checkbox("Mark as completed", key=f"complete_{selected_habit}")

        # Add value input if goal type is numeric
        value = None
        if habit_data['goal_type'] == 'numeric':
            value = st.number_input("Enter value", min_value=0.0, step=0.1)

        if st.button("Save Progress"):
            st.session_state.habit_manager.track_habit(selected_habit, today, completed, value)
            st.success("Progress saved!")

    with col2:
        # Display streak and stats
        streak = st.session_state.habit_manager.get_streak(selected_habit)
        st.metric("Current Streak", f"{streak} days")

    with col3:
        # Display goal progress
        goal_progress = st.session_state.habit_manager.get_goal_progress(selected_habit)
        st.metric("Goal Progress", f"{goal_progress:.1f}%")

    # Get tracking data
    tracking_data = st.session_state.habit_manager.get_tracking_data(selected_habit)

    # Statistics section
    st.subheader("Statistics")
    stats = calculate_completion_stats(tracking_data)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Days Tracked", stats['total_days'])
    with col2:
        st.metric("Days Completed", stats['completed_days'])
    with col3:
        st.metric("Completion Rate", f"{stats['completion_rate']}%")

    # Visualizations
    st.subheader("Visualizations")

    # Progress gauge
    progress_chart = create_progress_chart(stats['completion_rate'])
    st.plotly_chart(progress_chart, use_container_width=True)

    # Streak timeline
    streak_chart = create_streak_chart(tracking_data, habit_name)
    st.plotly_chart(streak_chart, use_container_width=True)

    # Completion heatmap
    heatmap = create_completion_heatmap(tracking_data, habit_name)
    st.plotly_chart(heatmap, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>Built with Streamlit | Track your habits, build better routines</p>
    </div>
    """,
    unsafe_allow_html=True
)
