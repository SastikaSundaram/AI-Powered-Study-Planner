from datetime import date, timedelta
import random
import plotly.graph_objects as go
from database import get_session
from models import StudyPlan

def generate_spaced_repetition_schedule(subject, difficulty, exam_date):
    """Generate a spaced repetition schedule based on difficulty and exam date"""
    days_remaining = (exam_date - date.today()).days
    
    if days_remaining <= 7:
        return [1, 3, 5, 7]
    
    difficulty_factor = {"easy": 0.8, "medium": 1.0, "hard": 1.2}[difficulty]
    
    intervals = [
        max(1, int(1 * difficulty_factor)),
        max(2, int(3 * difficulty_factor)),
        max(4, int(7 * difficulty_factor)),
        max(8, int(14 * difficulty_factor))
    ]
    
    if intervals[-1] > days_remaining:
        intervals = [max(1, int(days_remaining * i/4)) for i in range(1, 5)]
    
    return intervals

def generate_ai_study_plan(subject_details, motivation, energy, study_hours, exam_date):
    if not subject_details:
        return "Error: No subjects provided", []
    
    days_remaining = (exam_date - date.today()).days
    if days_remaining <= 0:
        return "Error: Goal date must be in the future", []
    
    weight_map = {
        "priority": {"low": 1, "medium": 2, "high": 3},
        "difficulty": {"easy": 0.8, "medium": 1.2, "hard": 1.5}
    }
    
    total_weight = 0
    for subject in subject_details:
        priority_weight = weight_map["priority"][subject["priority"]]
        difficulty_weight = weight_map["difficulty"][subject["difficulty"]]
        subject["weight"] = priority_weight * difficulty_weight
        total_weight += subject["weight"]
    
    if total_weight == 0:
        return "Error: Invalid subject weights", []
    
    energy_factor = {"low": 0.7, "medium": 1.0, "high": 1.3}[energy]
    motivation_factor = motivation / 7.0
    
    plan = []
    for subject in subject_details:
        hours = (subject["weight"] / total_weight) * study_hours * energy_factor * motivation_factor
        hours = round(max(0.5, min(study_hours, hours)), 1)
        
        days_per_week = max(2, min(5, int(hours * 3)))
        study_days = random.sample(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], days_per_week)
        
        plan.append({
            "subject": subject["subject"],
            "hours": hours,
            "priority": subject["priority"],
            "difficulty": subject["difficulty"],
            "study_days": study_days,
            "repetition_schedule": generate_spaced_repetition_schedule(
                subject["subject"],
                subject["difficulty"],
                exam_date
            )
        })
    
    priority_order = {"high": 0, "medium": 1, "low": 2}
    plan.sort(key=lambda x: (priority_order[x["priority"]], x["difficulty"]))
    
    return "Plan generated successfully!", plan

def save_user_state(user_id, plan):
    session = get_session()
    try:
        session.query(StudyPlan).filter_by(user_id=user_id).delete()
        
        for item in plan:
            plan_item = StudyPlan(
                user_id=user_id,
                subject=item["subject"],
                hours=item["hours"],
                priority=item["priority"],
                difficulty=item["difficulty"],
                study_days=",".join(item["study_days"])
            )
            session.add(plan_item)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def load_user_state(user_id):
    session = get_session()
    try:
        plan_items = session.query(StudyPlan).filter_by(user_id=user_id).all()
        if not plan_items:
            return None
        
        plan = []
        for item in plan_items:
            plan.append({
                "subject": item.subject,
                "hours": item.hours,
                "priority": item.priority,
                "difficulty": item.difficulty,
                "study_days": item.study_days.split(",")
            })
        return plan
    finally:
        session.close()

def create_progress_chart(plan):
    if not plan:
        return go.Figure()
    
    subjects = [entry["subject"] for entry in plan]
    hours = [entry["hours"] for entry in plan]
    colors = []
    
    for entry in plan:
        if entry["priority"] == "high":
            colors.append("#ef5350")
        elif entry["priority"] == "medium":
            colors.append("#ffa726")
        else:
            colors.append("#66bb6a")
    
    fig = go.Figure(go.Bar(
        x=subjects,
        y=hours,
        marker_color=colors,
        text=hours,
        textposition="auto"
    ))
    
    fig.update_layout(
        title="Study Time Allocation",
        xaxis_title="Subjects",
        yaxis_title="Daily Hours",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="x"
    )
    
    return fig

def recommend_resources(subjects):
    resources = {
        "Mathematics": [
            "https://www.khanacademy.org/math",
            "https://www.wolframalpha.com/"
        ],
        "Machine Learning": [
            "https://www.coursera.org/learn/machine-learning",
            "https://developers.google.com/machine-learning/crash-course"
        ],
        "Statistics": [
            "https://www.khanacademy.org/math/statistics-probability",
            "https://www.statlearning.com/"
        ],
        "Python": [
            "https://www.learnpython.org/",
            "https://realpython.com/"
        ],
        "Data Science": [
            "https://www.datacamp.com/",
            "https://www.kaggle.com/learn"
        ],
        "Physics": [
            "https://www.khanacademy.org/science/physics",
            "https://phet.colorado.edu/"
        ],
        "Chemistry": [
            "https://www.khanacademy.org/science/chemistry",
            "https://www.chemguide.co.uk/"
        ],
        "Biology": [
            "https://www.khanacademy.org/science/biology",
            "https://www.biologycorner.com/"
        ]
    }
    
    recommended = {}
    for subject in subjects:
        best_match = None
        for key in resources:
            if key.lower() in subject.lower() or subject.lower() in key.lower():
                best_match = key
                break
        
        if best_match:
            recommended[subject] = random.choice(resources[best_match])
        else:
            recommended[subject] = f"https://www.google.com/search?q={subject.replace(' ', '+')}+learning+resources"
    
    return recommended