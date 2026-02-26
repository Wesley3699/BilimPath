from sqlalchemy import Column, String, Float, Integer, Boolean, Text, DateTime, Enum, ForeignKey, SmallInteger, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.ext.declarative import declarative_base
from uuid import uuid4
from datetime import datetime
import enum

class Base(DeclarativeBase):
    pass

class UserRole(str, enum.Enum):
    student = "student"
    teacher = "teacher"


class SessionStatus(str, enum.Enum):
    testing    = "testing"
    explaining = "explaining"
    practicing = "practicing"
    retesting  = "retesting"
    completed  = "completed"

class AnswerType(str, enum.Enum):
    multiple_choice = "multiple_choice"
    open_text = "open_text"
    photo = "photo"
    document = "document"

class Institution(Base):
    __tablename__ = "institutions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    short_code = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    users = relationship("User", back_populates="institution")
    groups = relationship("Group", back_populates="institution")

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.student)
    full_name = Column(String(255), nullable=False)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    institution = relationship("Institution", back_populates="users")
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False)
    teacher_profile = relationship("TeacherProfile", back_populates="user", uselist=False)
    groups_owned = relationship("Group", back_populates="teacher")
    group_memberships = relationship("GroupMember", back_populates="user")
    subjects_created  = relationship("Subject", back_populates="created_by_user")
    learning_sessions = relationship("LearningSession", back_populates="student")
    exam_attempts     = relationship("ExamAttempt", back_populates="student")
    topic_masteries   = relationship("StudentTopicMastery", back_populates="student")
    error_history     = relationship("ErrorHistory", back_populates="student")


class StudentProfile(Base):
    __tablename__ = "student_profiles"
    user_id  = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=True)

    user  = relationship("User", back_populates="student_profile")
    group = relationship("Group", back_populates="students")


class TeacherProfile(Base):
    __tablename__ = "teacher_profiles"
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)

    user = relationship("User", back_populates="teacher_profile")

class Group(Base):
    __tablename__ = "groups"
    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name        = Column(String(100), nullable=False)
    teacher_id  = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    institution_id  = Column(UUID(as_uuid=True), ForeignKey("institutions.id"), nullable=True)
    invite_code = Column(String(10), unique=True, nullable=False)

    institution  = relationship("Institution", back_populates="groups")
    teacher  = relationship("User", back_populates="groups_owned")
    students = relationship("StudentProfile", back_populates="group")
    members  = relationship("GroupMember", back_populates="group")


class GroupMember(Base):
    __tablename__ = "group_members"
    group_id  = Column(UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True)
    user_id   = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    joined_at = Column(DateTime, server_default=func.now())
    
    group = relationship("Group", back_populates="members")
    user  = relationship("User", back_populates="group_memberships")

class Subject(Base):
    __tablename__ = "subjects"
    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name       = Column(String(255), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    created_by_user   = relationship("User", back_populates="subjects_created")
    topics            = relationship("Topic", back_populates="subject")
    learning_sessions = relationship("LearningSession", back_populates="subject")



class Topic(Base):
    __tablename__ = "topics"
    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    parent_id  = Column(UUID(as_uuid=True), ForeignKey("topics.id"), nullable=True)
    title      = Column(String(255), nullable=False)
    order_num  = Column(Integer, default=0)
    
    subject   = relationship("Subject", back_populates="topics")
    parent    = relationship("Topic", back_populates="children", remote_side=[id])
    children  = relationship("Topic", back_populates="parent")
    exams     = relationship("Exam", back_populates="topic")
    masteries = relationship("StudentTopicMastery", back_populates="topic")
    errors    = relationship("ErrorHistory", back_populates="topic")


class LearningSession(Base):
    __tablename__ = "learning_sessions"
    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    student_id   = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    subject_id   = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)
    status       = Column(Enum(SessionStatus), default=SessionStatus.testing)
    started_at   = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    student = relationship("User", back_populates="learning_sessions")
    subject = relationship("Subject", back_populates="learning_sessions")
    exams   = relationship("Exam", back_populates="session")


class Exam(Base):
    __tablename__ = "exams"
    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("learning_sessions.id"), nullable=False)
    topic_id   = Column(UUID(as_uuid=True), ForeignKey("topics.id"), nullable=True)
    difficulty = Column(SmallInteger, default=3)
    questions  = Column(JSONB, nullable=False)
    is_retest  = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    
    session  = relationship("LearningSession", back_populates="exams")
    topic    = relationship("Topic", back_populates="exams")
    attempts = relationship("ExamAttempt", back_populates="exam")

class ExamAttempt(Base):
    __tablename__ = "exam_attempts"
    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    exam_id      = Column(UUID(as_uuid=True), ForeignKey("exams.id"), nullable=False)
    student_id   = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    answers      = Column(JSONB, nullable=True)
    file_url     = Column(Text, nullable=True)
    answer_type  = Column(Enum(AnswerType), default=AnswerType.multiple_choice)
    score        = Column(Float, nullable=True)
    submitted_at = Column(DateTime, server_default=func.now())
    
    exam     = relationship("Exam", back_populates="attempts")
    student  = relationship("User", back_populates="exam_attempts")
    analysis = relationship("AiAnalysis", back_populates="attempt", uselist=False)


class AiAnalysis(Base):
    __tablename__ = "ai_analysis"
    id               = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    attempt_id       = Column(UUID(as_uuid=True), ForeignKey("exam_attempts.id", ondelete="CASCADE"), unique=True, nullable=False)
    score            = Column(Float, nullable=True)
    errors_breakdown = Column(JSONB, nullable=True)
    weak_topics      = Column(JSONB, nullable=True)
    explanation      = Column(Text, nullable=True)
    recommendations  = Column(Text, nullable=True)
    extra_tasks      = Column(JSONB, nullable=True)
    created_at       = Column(DateTime, server_default=func.now())
    
    attempt = relationship("ExamAttempt", back_populates="analysis")


class StudentTopicMastery(Base):
    __tablename__ = "student_topic_mastery"
    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    student_id     = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    topic_id       = Column(UUID(as_uuid=True), ForeignKey("topics.id"), nullable=False)
    mastery_level  = Column(Float, default=0.0)
    confidence     = Column(Float, default=0.0)
    attempts_count = Column(Integer, default=0)
    last_tested_at = Column(DateTime, nullable=True)
    
    __table_args__ = (
        UniqueConstraint("student_id", "topic_id", name="uq_student_topic"),
    )
    
    student = relationship("User", back_populates="topic_masteries")
    topic   = relationship("Topic", back_populates="masteries")

class ErrorHistory(Base):
    __tablename__ = "error_history"
    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    topic_id   = Column(UUID(as_uuid=True), ForeignKey("topics.id"), nullable=False)
    question   = Column(Text, nullable=True)
    error_type = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    student = relationship("User", back_populates="error_history")
    topic   = relationship("Topic", back_populates="errors")



class Course(Base):
    __tablename__ = "courses"
    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title          = Column(String(255), nullable=False)
    description    = Column(Text, nullable=True)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id"), nullable=True)
    created_by     = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    is_active      = Column(Boolean, default=True)
    created_at     = Column(DateTime, server_default=func.now())

    lessons     = relationship("Lesson", back_populates="course")
    enrollments = relationship("CourseEnrollment", back_populates="course")


class Lesson(Base):
    __tablename__ = "lessons"
    id               = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    course_id        = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    topic_id         = Column(UUID(as_uuid=True), ForeignKey("topics.id"), nullable=True)
    title            = Column(String(255), nullable=False)
    description      = Column(Text, nullable=True)
    content          = Column(Text, nullable=True)
    video_url        = Column(Text, nullable=True)
    duration_minutes = Column(Integer, default=0)
    order_num        = Column(Integer, default=0)
    is_published     = Column(Boolean, default=False)
    created_at       = Column(DateTime, server_default=func.now())

    course    = relationship("Course", back_populates="lessons")
    topic     = relationship("Topic")
    progress  = relationship("LessonProgress", back_populates="lesson")


class LessonProgress(Base):
    __tablename__ = "lesson_progress"
    id               = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    lesson_id        = Column(UUID(as_uuid=True), ForeignKey("lessons.id"), nullable=False)
    student_id       = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status           = Column(String(50), default="not_started")
    progress_percent = Column(Float, default=0.0)
    started_at       = Column(DateTime, nullable=True)
    completed_at     = Column(DateTime, nullable=True)
    last_accessed_at = Column(DateTime, nullable=True)

    lesson  = relationship("Lesson", back_populates="progress")


class CourseEnrollment(Base):
    __tablename__ = "course_enrollments"
    course_id  = Column(UUID(as_uuid=True), ForeignKey("courses.id"), primary_key=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    enrolled_at = Column(DateTime, server_default=func.now())

    course = relationship("Course", back_populates="enrollments")