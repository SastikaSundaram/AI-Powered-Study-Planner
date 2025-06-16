import streamlit as st
import time
from datetime import datetime, timedelta
import json
import os
import random

POMODORO_FILE = "pomodoro_sessions.json"

def save_session(start_time, end_time, session_type):
    session = {
        "start": start_time.isoformat(),
        "end": end_time.isoformat(),
        "type": session_type
    }
    
    sessions = []
    if os.path.exists(POMODORO_FILE):
        with open(POMODORO_FILE, "r") as f:
            sessions = json.load(f)
    
    sessions.append(session)
    
    with open(POMODORO_FILE, "w") as f:
        json.dump(sessions, f)

def load_sessions():
    if os.path.exists(POMODORO_FILE):
        with open(POMODORO_FILE, "r") as f:
            return json.load(f)
    return []

def show_pomodoro_timer():
    st.subheader("🍅 Pomodoro Timer")
    st.caption("Work in focused 25-minute intervals with 5-minute breaks")
    
    # Initialize session state
    if 'timer_running' not in st.session_state:
        st.session_state.timer_running = False
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    if 'end_time' not in st.session_state:
        st.session_state.end_time = None
    if 'session_type' not in st.session_state:
        st.session_state.session_type = "Work"
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        session_type = st.radio("Session Type", ["Work", "Break"], index=0 if st.session_state.session_type == "Work" else 1)
        session_length = st.slider("Minutes", 1, 60, 25 if session_type == "Work" else 5)
    
    with col2:
        time_placeholder = st.empty()
        status_placeholder = st.empty()
        button_placeholder = st.empty()
    
    if st.session_state.timer_running:
        elapsed = datetime.now() - st.session_state.start_time
        remaining = st.session_state.end_time - datetime.now()
        
        if remaining.total_seconds() <= 0:
            st.session_state.timer_running = False
            save_session(
                st.session_state.start_time,
                datetime.now(),
                st.session_state.session_type
            )
            st.session_state.start_time = None
            st.session_state.end_time = None
            st.experimental_rerun()
        
        minutes, seconds = divmod(int(remaining.total_seconds()), 60)
        time_placeholder.metric("Time Remaining", f"{minutes:02d}:{seconds:02d}")
        status_placeholder.info(f"⏳ {st.session_state.session_type} session in progress...")
        
        if button_placeholder.button("Stop Session"):
            st.session_state.timer_running = False
            save_session(
                st.session_state.start_time,
                datetime.now(),
                st.session_state.session_type
            )
            st.session_state.start_time = None
            st.session_state.end_time = None
            st.experimental_rerun()
    else:
        time_placeholder.metric("Ready to Start", f"{session_length:02d}:00")
        status_placeholder.info("Click Start to begin your session")
        
        if button_placeholder.button("Start Session"):
            st.session_state.timer_running = True
            st.session_state.start_time = datetime.now()
            st.session_state.end_time = datetime.now() + timedelta(minutes=session_length)
            st.session_state.session_type = session_type
            st.experimental_rerun()
    
    # Session history
    st.subheader("Session History")
    sessions = load_sessions()
    
    if sessions:
        # Calculate stats
        work_sessions = sum(1 for s in sessions if s['type'] == 'Work')
        break_sessions = sum(1 for s in sessions if s['type'] == 'Break')
        
        # Fixed: Corrected parentheses mismatch
        total_work_minutes = sum(
            (datetime.fromisoformat(s['end']) - datetime.fromisoformat(s['start'])).total_seconds() / 60
            for s in sessions if s['type'] == 'Work'
        )
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Work Sessions", work_sessions)
        col2.metric("Break Sessions", break_sessions)
        col3.metric("Total Work Time", f"{total_work_minutes:.1f} min")
        
        # Show recent sessions
        st.write("Recent Sessions:")
        for session in sessions[-5:]:
            start = datetime.fromisoformat(session['start']).strftime("%Y-%m-%d %H:%M")
            end = datetime.fromisoformat(session['end']).strftime("%H:%M")
            duration = (datetime.fromisoformat(session['end']) - datetime.fromisoformat(session['start'])).seconds // 60
            st.caption(f"🕒 {start} to {end} | {session['type']} session | {duration} min")
    else:
        st.info("No sessions recorded yet. Start a session to see your history.")
    
    # Pomodoro technique explanation
    with st.expander("About the Pomodoro Technique"):
        st.markdown("""
        The Pomodoro Technique is a time management method developed by Francesco Cirillo. 
        It uses a timer to break work into intervals, traditionally 25 minutes in length, 
        separated by short breaks (5 minutes).
        
        **How to use it:**
        1. Choose a task to work on
        2. Set the timer for 25 minutes (work session)
        3. Work on the task until the timer rings
        4. Take a short 5-minute break
        5. Every 4 work sessions, take a longer break (15-30 minutes)
        
        Benefits:
        - Improves focus and concentration
        - Reduces mental fatigue
        - Helps prevent burnout
        - Increases productivity
        """)

def show_study_techniques(subject_difficulty=None):
    st.subheader("🧠 Study Techniques")
    
    techniques = {
        "Spaced Repetition": {
            "description": "Review information at increasing intervals over time",
            "how_to": "1. Review material immediately after learning\n2. Review again after 1 day\n3. Review after 3 days\n4. Review after 1 week\n5. Review after 1 month",
            "best_for": "Memorizing facts, vocabulary, concepts"
        },
        "Active Recall": {
            "description": "Actively retrieve information from memory rather than passively reviewing",
            "how_to": "1. Study the material\n2. Close your books\n3. Write down or explain everything you remember\n4. Check what you missed\n5. Repeat until you recall everything",
            "best_for": "Understanding complex concepts, exam preparation"
        },
        "Feynman Technique": {
            "description": "Explain concepts in simple terms as if teaching a child",
            "how_to": "1. Choose a concept to learn\n2. Explain it in simple terms\n3. Identify gaps in your explanation\n4. Review and simplify further\n5. Teach it to someone else",
            "best_for": "Understanding difficult concepts, identifying knowledge gaps"
        },
        "Interleaving": {
            "description": "Mix different topics or subjects during study sessions",
            "how_to": "1. Study multiple related topics in one session\n2. Alternate between topics\n3. Make connections between concepts\n4. Practice switching between different types of problems",
            "best_for": "Problem-solving, applying concepts to new situations"
        }
    }
    
    # Recommendation based on difficulty
    if subject_difficulty:
        difficulty_map = {
            "easy": ["Spaced Repetition", "Active Recall"],
            "medium": ["Feynman Technique", "Interleaving"],
            "hard": ["Feynman Technique", "Active Recall"]
        }
        
        rec_techniques = difficulty_map.get(subject_difficulty.lower(), list(techniques.keys()))
        st.info(f"Recommended for {subject_difficulty} subjects: {', '.join(rec_techniques)}")
    
    # Display all techniques
    for name, info in techniques.items():
        with st.expander(f"**{name}** - {info['description']}"):
            st.write(f"**How to use:**\n{info['how_to']}")
            st.write(f"**Best for:** {info['best_for']}")
    
    # Psychology of learning
    with st.expander("The Science Behind Effective Learning"):
        st.markdown("""
        Research-backed learning principles:
        
        **1. Desirable Difficulty**
        - Learning should be challenging but achievable
        - The harder your brain works to retrieve information, the stronger the memory
        
        **2. Elaboration**
        - Connect new information to what you already know
        - Ask "why" questions to deepen understanding
        
        **3. Dual Coding**
        - Combine words and visuals for better retention
        - Create diagrams, mind maps, and visual representations
        
        **4. Concrete Examples**
        - Abstract concepts are easier to remember with concrete examples
        - Create multiple examples for each concept
        
        **5. Retrieval Practice**
        - Regularly test yourself on what you've learned
        - Flashcards, practice tests, and self-explanation are effective methods
        """)

def show_motivational_tools():
    st.subheader("💪 Motivational Tools")
    
    # Quotes
    quotes = [
        "The expert in anything was once a beginner.",
        "Don't watch the clock; do what it does. Keep going.",
        "The secret of getting ahead is getting started.",
        "You don't have to be great to start, but you have to start to be great.",
        "The only way to learn mathematics is to do mathematics.",
        "Every expert was once a beginner. Every pro was once an amateur.",
        "Small progress is still progress. Keep going.",
        "The more you practice, the better you get. The better you get, the more you enjoy it.",
        "Success is the sum of small efforts, repeated day in and day out.",
        "The best time to plant a tree was 20 years ago. The second best time is now."
    ]
    
    st.write("### Daily Inspiration")
    st.success(f"✨ \"{st.session_state.get('daily_quote', random.choice(quotes))}\"")
    
    if st.button("New Quote"):
        st.session_state.daily_quote = random.choice(quotes)
        st.experimental_rerun()
    
    # Focus music
    st.write("### Focus Music")
    st.caption("Background music to enhance concentration")
    
    music_options = {
        "Lofi Hip Hop": "https://www.youtube.com/watch?v=jfKfPfyJRdk",
        "Classical Piano": "https://www.youtube.com/watch?v=W6YNA7Q0wDc",
        "Nature Sounds": "https://www.youtube.com/watch?v=H6G4rH7XfZc",
        "Binaural Beats": "https://www.youtube.com/watch?v=wzjWIxXBs_s",
        "Jazz for Focus": "https://www.youtube.com/watch?v=W4Ov8q9L-1Q"
    }
    
    selected_music = st.selectbox("Choose music type", list(music_options.keys()))
    st.video(music_options[selected_music])
    
    # Study environment tips
    with st.expander("Optimize Your Study Environment"):
        st.markdown("""
        **Create an ideal study space:**
        
        - 🪑 Use a comfortable chair and proper desk height
        - 💡 Ensure adequate lighting (natural light is best)
        - 🔇 Minimize distractions (use noise-cancelling headphones if needed)
        - 🌡️ Maintain comfortable temperature (20-22°C / 68-72°F)
        - 🚰 Keep water nearby to stay hydrated
        - 🍎 Have healthy snacks available
        - 📱 Put your phone on Do Not Disturb mode
        - 🧹 Keep your space clean and organized
        
        **Pro tip:** Use different locations for different subjects to create mental associations.
        """)

def show_mindfulness_break():
    st.subheader("🧘 Mindfulness Break")
    st.caption("Take a short break to refresh your mind")
    
    if st.button("Start 3-Minute Breathing Exercise"):
        with st.spinner("Find a comfortable position..."):
            time.sleep(1)
            st.info("Close your eyes and take a deep breath in...")
            time.sleep(4)
            st.info("Slowly exhale... Release all tension...")
            time.sleep(4)
            st.info("Focus on your breath... Inhale slowly...")
            time.sleep(4)
            st.info("Exhale completely... Let go of distractions...")
            time.sleep(4)
            st.info("Continue breathing naturally... Notice how you feel...")
            time.sleep(4)
            st.info("Gently bring your awareness back...")
            time.sleep(2)
            st.success("Exercise complete! Notice how you feel more centered and focused.")