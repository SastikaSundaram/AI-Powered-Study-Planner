from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import datetime
import hashlib

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True, nullable=False)
    password = Column(String(150), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password):
        return self.password == hashlib.sha256(password.encode()).hexdigest()

class StudyPlan(Base):
    __tablename__ = 'study_plans'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    subject = Column(String(150), nullable=False)
    hours = Column(Float, nullable=False)
    priority = Column(String(50), nullable=False)
    difficulty = Column(String(50), nullable=False)
    study_days = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Progress(Base):
    __tablename__ = 'progress'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    subject = Column(String(150), nullable=False)
    date = Column(Date, nullable=False)
    hours_studied = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)