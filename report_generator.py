from fpdf import FPDF
from datetime import datetime, timedelta
import pandas as pd
import os
import tempfile

def generate_study_report(user, plan, exam_date, resources, focus_data):
    # Create PDF report
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="AI-Powered Study Plan Report", ln=1, align="C")
    pdf.ln(10)
    
    # User info
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt=f"Student: {user.username}", ln=1)
    pdf.cell(200, 10, txt=f"Generated on: {datetime.now().strftime('%B %d, %Y')}", ln=1)
    pdf.cell(200, 10, txt=f"Exam Date: {exam_date.strftime('%B %d, %Y')}", ln=1)
    days_remaining = (exam_date - datetime.now().date()).days
    pdf.cell(200, 10, txt=f"Days Remaining: {days_remaining}", ln=1)
    pdf.ln(10)
    
    # Study plan table
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Daily Study Plan", ln=1)
    pdf.set_font("Arial", size=10)
    
    # Table header
    col_widths = [60, 30, 30, 30, 40]
    headers = ["Subject", "Priority", "Difficulty", "Hours/Day", "Study Days"]
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, 1)
    pdf.ln()
    
    # Table rows
    for item in plan:
        pdf.cell(col_widths[0], 10, item['subject'], 1)
        pdf.cell(col_widths[1], 10, item['priority'], 1)
        pdf.cell(col_widths[2], 10, item['difficulty'], 1)
        pdf.cell(col_widths[3], 10, str(item['hours']), 1)
        pdf.cell(col_widths[4], 10, ", ".join(item['study_days']), 1)
        pdf.ln()
    
    pdf.ln(10)
    
    # Resources
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "Recommended Resources", ln=1)
    pdf.set_font("Arial", size=10)
    for subject, url in resources.items():
        pdf.cell(200, 10, f"{subject}: {url}", ln=1)
    
    # Focus analytics
    if focus_data:
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, "Focus Analytics", ln=1)
        pdf.set_font("Arial", size=10)
        
        total_minutes = sum(s['duration'] for s in focus_data)
        avg_duration = total_minutes / len(focus_data)
        
        pdf.cell(200, 10, f"Total Focus Time: {total_minutes:.0f} minutes", ln=1)
        pdf.cell(200, 10, f"Average Session: {avg_duration:.1f} minutes", ln=1)
        pdf.cell(200, 10, f"Sessions Completed: {len(focus_data)}", ln=1)
    
    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf.output(temp_file.name)
    return temp_file.name

def generate_study_schedule_csv(plan):
    # Create a weekly schedule
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    schedule = {day: [] for day in days}
    
    for subject in plan:
        for day in subject['study_days']:
            if day in days:
                schedule[day].append(f"{subject['subject']} ({subject['hours']}h)")
    
    # Create CSV content
    csv_content = "Day,Subjects\n"
    for day in days:
        subjects = "; ".join(schedule[day]) if schedule[day] else "Rest day"
        csv_content += f"{day},{subjects}\n"
    
    return csv_content