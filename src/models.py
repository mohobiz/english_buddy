from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Table, Integer, JSON, create_engine
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.types import ARRAY
from pgvector.sqlalchemy import Vector
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class UserProfile(Base):
    __tablename__ = 'user_profiles'
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    username = Column(String, nullable=False)
    email = Column(String, nullable=True)
    proficiency_level = Column(String, nullable=False)
    learning_goals = Column(ARRAY(String), nullable=False)
    preferred_topics = Column(ARRAY(String), nullable=False)
    registration_date = Column(DateTime, nullable=False)
    last_active = Column(DateTime, nullable=False)

class ConversationLog(Base):
    __tablename__ = 'conversation_logs'
    log_id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=True), ForeignKey('user_profiles.user_id'))
    agent_interactions = Column(JSONB, nullable=False)  # List of AgentInteraction dicts
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    total_duration = Column(Float, nullable=False)  # seconds
    key_metrics = Column(JSONB, nullable=False)
    embedding = Column(Vector(1536), nullable=True)  # For semantic search

class AgentFeedback(Base):
    __tablename__ = 'agent_feedback'
    feedback_id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=True), ForeignKey('user_profiles.user_id'))
    agent_name = Column(String, nullable=False)
    feedback_type = Column(String, nullable=False)  # grammar, vocabulary, pronunciation
    detailed_feedback = Column(JSONB, nullable=False)
    improvement_score = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)

class AssessmentResult(Base):
    __tablename__ = 'assessment_results'
    assessment_id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=True), ForeignKey('user_profiles.user_id'))
    quiz_type = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False)
    detailed_breakdown = Column(JSONB, nullable=False)
    skills_assessed = Column(ARRAY(String), nullable=False)
    timestamp = Column(DateTime, nullable=False)

class LearningPath(Base):
    __tablename__ = 'learning_paths'
    user_id = Column(UUID(as_uuid=True), ForeignKey('user_profiles.user_id'), primary_key=True)
    current_focus_areas = Column(ARRAY(String), nullable=False)
    recommended_exercises = Column(JSONB, nullable=False)  # List of Exercise dicts
    progress_percentage = Column(JSONB, nullable=False)  # Dict[str, float]
    next_recommended_action = Column(String, nullable=False)
    last_updated = Column(DateTime, nullable=False) 