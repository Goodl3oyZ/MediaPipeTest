"""Database models for Virtual Trainer AI."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="user")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    results = relationship("ExerciseResult", back_populates="user")
    jobs = relationship("JobAudit", back_populates="user")


class ExerciseResult(Base):
    __tablename__ = "exercise_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    label = Column(String(255), nullable=False)
    score = Column(String(50))
    feedback = Column(Text)
    input_video_key = Column(String(255))
    output_video_key = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="results")


class JobAudit(Base):
    __tablename__ = "job_audit"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(String(255), index=True, nullable=False)
    status = Column(String(50), default="queued")
    input_key = Column(String(255), nullable=False)
    output_key = Column(String(255))
    error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="jobs")
