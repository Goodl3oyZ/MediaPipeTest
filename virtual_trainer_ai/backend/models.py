# models.py
# กำหนด ORM models สำหรับ User, ExerciseResult, SampleVideo
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    display_name = Column(String)
    goal = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    # ความสัมพันธ์กับผลการฝึก
    results = relationship("ExerciseResult", back_populates="user")

class ExerciseResult(Base):
    __tablename__ = "exercise_results"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    exercise_type = Column(String)
    input_video_path = Column(Text)
    output_video_path = Column(Text)
    feedback = Column(Text)
    score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    # ความสัมพันธ์กับ user
    user = relationship("User", back_populates="results")

class SampleVideo(Base):
    __tablename__ = "sample_videos"
    id = Column(Integer, primary_key=True, index=True)
    exercise_type = Column(String)
    file_path = Column(Text)