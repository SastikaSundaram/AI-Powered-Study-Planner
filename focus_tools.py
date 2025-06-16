import streamlit as st
import time
import random
import json
import os
from datetime import datetime, timedelta
import plotly.graph_objects as go

FOCUS_SESSIONS_FILE = "focus_sessions.json"
BLOCKED_SITES_FILE = "blocked_sites.json"

def init_focus_files():
    if not os.path.exists(FOCUS_SESSIONS_FILE):
        with open(FOCUS_SESSIONS_FILE, "w") as f:
            json.dump([], f)
    
    if not os.path.exists(BLOCKED_SITES_FILE):
        with open(BLOCKED_SITES_FILE, "w") as f:
            json.dump([], f)

def save_focus_session(start, end, distractions=0):
    session = {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "duration": (end - start).total_seconds() / 60,
        "distractions": distractions
    }
    
    sessions = []
    if os.path.exists(FOCUS_SESSIONS_FILE):
        with open(FOCUS_SESSIONS_FILE, "r") as f:
            sessions = json.load(f)
    
    sessions.append(session)
    
    with open(FOCUS_SESSIONS_FILE, "w") as f:
        json.dump(sessions, f)

def get_focus_sessions():
    if os.path.exists(FOCUS_SESSIONS_FILE):
        with open(FOCUS_SESSIONS_FILE, "r") as f:
            return json.load(f)
    return []

def get_blocked_sites():
    if os.path.exists(BLOCKED_SITES_FILE):
        with open(BLOCKED_SITES_FILE, "r") as f:
            return json.load(f)
    return []

def add_blocked_site(site):
    sites = get_blocked_sites()
    if site not in sites:
        sites.append(site)
        with open(BLOCKED_SITES_FILE, "w") as f:
            json.dump(sites, f)

def remove_blocked_site(site):
    sites = get_blocked_sites()
    if site in sites:
        sites.remove(site)
        with open(BLOCKED_SITES_FILE, "w") as f:
            json.dump(sites, f)

def show_focus_mode():
    st.subheader("🚀 Deep Focus Mode")
    st.caption("Minimize distractions and maximize productivity")
    
    # Initialize session state
    if 'focus_active' not in st.session_state:
        st.session_state.focus_active = False
    if 'focus_start' not in st.session_state:
        st.session_state.focus_start = None
    if 'distraction_count' not in st.session_state:
        st.session_state.distraction_count = 0
    
    # Focus mode activation
    if not st.session_state.focus_active:
        goal = st.number_input("Set focus duration (minutes)", 15, 120, 45)
        st.info("Focus mode will:")
        st.write("- Hide non-essential UI elements")
        st.write("- Block distracting websites (via browser extension)")
        st.write("- Track your focused time")
        st.write("- Minimize visual distractions")
        
        if st.button("Activate Deep Focus"):
            st.session_state.focus_active = True
            st.session_state.focus_start = datetime.now()
            st.session_state.focus_goal = goal
            st.session_state.distraction_count = 0
            st.experimental_rerun()
    else:
        elapsed = datetime.now() - st.session_state.focus_start
        elapsed_minutes = elapsed.total_seconds() / 60
        progress = min(100, (elapsed_minutes / st.session_state.focus_goal) * 100)
        
        # Create distraction-free interface
        st.markdown("""
        <style>
            header { visibility: hidden; }
            .stDeployButton { display: none; }
            section[data-testid="stSidebar"] { display: none; }
            .stApp { margin: 0; padding: 0; }
            .main .block-container { padding: 1rem; max-width: 100% !important; }
        </style>
        """, unsafe_allow_html=True)
        
        # Focus timer display
        st.progress(int(progress))
        minutes_left = max(0, st.session_state.focus_goal - elapsed_minutes)
        st.metric("Minutes Remaining", f"{minutes_left:.1f}", 
                 f"{elapsed_minutes:.1f} minutes focused")
        
        # Distraction tracking
        if st.button("I Got Distracted 😞"):
            st.session_state.distraction_count += 1
        
        st.write(f"Distractions: {st.session_state.distraction_count}")
        
        # End session button
        if st.button("End Focus Session Early"):
            save_focus_session(
                st.session_state.focus_start,
                datetime.now(),
                st.session_state.distraction_count
            )
            st.session_state.focus_active = False
            st.experimental_rerun()
        
        # Auto-end when goal reached
        if elapsed_minutes >= st.session_state.focus_goal:
            save_focus_session(
                st.session_state.focus_start,
                datetime.now(),
                st.session_state.distraction_count
            )
            st.session_state.focus_active = False
            st.balloons()
            st.success("🎉 Focus session completed successfully!")
            time.sleep(2)
            st.experimental_rerun()

def show_website_blocker():
    st.subheader("🚫 Website Blocker")
    st.caption("Block distracting websites during study sessions")
    
    sites = get_blocked_sites()
    new_site = st.text_input("Add website to block (e.g. youtube.com)")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Add Site") and new_site:
            add_blocked_site(new_site)
            st.experimental_rerun()
    
    if sites:
        st.write("Blocked Websites:")
        for site in sites:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"- {site}")
            with col2:
                if st.button(f"Remove", key=f"remove_{site}"):
                    remove_blocked_site(site)
                    st.experimental_rerun()
        
        st.download_button(
            "Export Block List",
            "\n".join(sites),
            file_name="blocked_sites.txt",
            help="Import into website blockers like BlockSite, Freedom, etc."
        )
    else:
        st.info("No websites blocked yet. Add sites you find distracting.")
    
    st.info("**How to use:** Install a website blocker extension and import this list")

def show_focus_analytics():
    sessions = get_focus_sessions()
    
    if not sessions:
        st.info("No focus sessions recorded yet")
        return
    
    # Calculate stats
    total_minutes = sum(s['duration'] for s in sessions)
    avg_duration = total_minutes / len(sessions)
    distractions = sum(s['distractions'] for s in sessions)
    avg_distractions = distractions / len(sessions)
    best_session = max(sessions, key=lambda x: x['duration'])
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Focus Time", f"{total_minutes:.0f} min")
    col2.metric("Avg. Session", f"{avg_duration:.1f} min")
    col3.metric("Avg. Distractions", f"{avg_distractions:.1f}/session")
    
    # Timeline
    st.subheader("Focus History")
    dates = [datetime.fromisoformat(s['start']).strftime("%Y-%m-%d") for s in sessions]
    durations = [s['duration'] for s in sessions]
    distractions = [s['distractions'] for s in sessions]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=dates,
        y=durations,
        name='Focus Duration',
        marker_color='#4CAF50'
    ))
    fig.add_trace(go.Scatter(
        x=dates,
        y=distractions,
        name='Distractions',
        mode='lines+markers',
        yaxis='y2',
        line=dict(color='#F44336')
    ))
    
    fig.update_layout(
        title='Focus Session History',
        xaxis_title='Date',
        yaxis_title='Duration (min)',
        yaxis2=dict(
            title='Distractions',
            overlaying='y',
            side='right'
        ),
        barmode='group'
    )
    st.plotly_chart(fig)
    
    # Recommendations
    st.subheader("Focus Insights")
    if avg_distractions > 3:
        st.warning("**High distraction rate detected:** Try using website blocking or changing study environment")
    if avg_duration < 30:
        st.info("**Short session length:** Consider using the Pomodoro technique to build focus stamina")
    
    st.write(f"**Longest session:** {best_session['duration']:.0f} min on {datetime.fromisoformat(best_session['start']).strftime('%b %d')}")
    
    with st.expander("Focus Improvement Tips"):
        st.markdown("""
        - **Eliminate digital distractions:** Use website blockers during study
        - **Physical environment:** Clean desk, proper lighting, comfortable temperature
        - **Time blocking:** Schedule specific times for specific subjects
        - **Single-tasking:** Focus on one task at a time
        - **Mindfulness:** Practice 5-minute meditation before studying
        - **Accountability:** Study with a partner or join a focus group
        """)

def show_concentration_exercises():
    st.subheader("🧠 Concentration Exercises")
    
    exercises = {
        "Breath Counting": {
            "steps": "1. Sit comfortably\n2. Breathe naturally\n3. Count each exhale (1 to 10)\n4. Repeat for 5 minutes",
            "benefit": "Improves focus and reduces anxiety"
        },
        "Pomodoro Technique": {
            "steps": "1. Set timer for 25 minutes\n2. Focus intensely\n3. Take 5-minute break\n4. Repeat",
            "benefit": "Builds focus stamina"
        },
        "The 5 More Rule": {
            "steps": "When you want to quit:\n1. Do 5 more minutes\n2. Solve 5 more problems\n3. Read 5 more pages",
            "benefit": "Builds mental endurance"
        },
        "Mindful Observation": {
            "steps": "1. Choose an object\n2. Observe it for 1 minute\n3. Note every detail\n4. Refocus attention when mind wanders",
            "benefit": "Trains attention control"
        }
    }
    
    selected = st.selectbox("Choose an exercise", list(exercises.keys()))
    
    st.write(f"**How to:**\n{exercises[selected]['steps']}")
    st.write(f"**Benefit:** {exercises[selected]['benefit']}")
    
    if st.button("Start 5-Minute Exercise"):
        with st.spinner("Preparing your mind for focus..."):
            time.sleep(1)
            st.info("Find a comfortable position...")
            time.sleep(1)
            st.info("Clear your mind...")
            time.sleep(1)
            st.info("Begin the exercise...")
            time.sleep(60)
            st.success("Exercise complete! Notice improved focus.")