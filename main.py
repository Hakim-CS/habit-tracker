import streamlit as st
import pandas as pd
from datetime import datetime
from data_manager import HabitManager
from visualizations import create_streak_chart, create_completion_heatmap, create_progress_chart
from utils import get_date_range, format_date, calculate_completion_stats

# Initialize session state
if 'habit_manager' not in st.session_state:
    st.session_state.habit_manager = HabitManager()

# Page configuration
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
    
    if st.button("Add Habit"):
        if new_habit_name:
            st.session_state.habit_manager.add_habit(new_habit_name, new_habit_desc)
            st.success(f"Added new habit: {new_habit_name}")
        else:
            st.error("Please enter a habit name")

    # About section
    st.markdown("---")
    st.header("About")
    st.markdown("""
        👨‍💻 **Abdul Hakim Nazari**  
        Computer Engineering Student  
        Pamukkale University

        📧 **Feedback & Contact**  
        [hakim.nazari.tech@gmail.com](mailto:hakim.nazari.tech@gmail.com)

        This habit tracker helps you build better routines through 
        visualization and progress tracking.
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
        format_func=lambda x: habits[habits['habit_id'] == x]['name'].iloc[0]
    )
    
    # Get habit details
    habit_name = habits[habits['habit_id'] == selected_habit]['name'].iloc[0]
    
    # Create columns for layout
    col1, col2 = st.columns(2)
    
    with col1:
        # Track today's habit
        st.subheader("Track Today")
        today = datetime.now().strftime('%Y-%m-%d')
        completed = st.checkbox("Mark as completed", key=f"complete_{selected_habit}")
        if st.button("Save Progress"):
            st.session_state.habit_manager.track_habit(selected_habit, today, completed)
            st.success("Progress saved!")
    
    with col2:
        # Display streak and stats
        streak = st.session_state.habit_manager.get_streak(selected_habit)
        st.metric("Current Streak", f"{streak} days")

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
        <p>Built with ❤️ using Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)