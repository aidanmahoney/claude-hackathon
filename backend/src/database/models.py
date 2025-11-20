"""Database models using SQLAlchemy"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


class CourseMonitor(Base):
    """Course monitor configuration"""
    __tablename__ = "course_monitors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    term = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    course_number = Column(String, nullable=False)
    section_id = Column(String, nullable=True)
    notify_on_open = Column(Boolean, default=True)
    notify_on_waitlist = Column(Boolean, default=False)
    check_interval = Column(Integer, default=300)
    active = Column(Boolean, default=True)
    last_checked = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    snapshots = relationship("EnrollmentSnapshot", back_populates="monitor", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="monitor", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CourseMonitor {self.subject} {self.course_number}>"


class EnrollmentSnapshot(Base):
    """Enrollment snapshot record"""
    __tablename__ = "enrollment_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    monitor_id = Column(Integer, ForeignKey("course_monitors.id", ondelete="CASCADE"), nullable=False)
    section_id = Column(String, nullable=False)
    class_number = Column(String, nullable=True)
    total_seats = Column(Integer, nullable=True)
    enrolled_seats = Column(Integer, nullable=True)
    open_seats = Column(Integer, nullable=True)
    waitlist_total = Column(Integer, nullable=True)
    waitlist_enrolled = Column(Integer, nullable=True)
    waitlist_open = Column(Integer, nullable=True)
    status = Column(String, nullable=True)
    instructor = Column(String, nullable=True)
    timestamp = Column(DateTime, server_default=func.now())

    # Relationships
    monitor = relationship("CourseMonitor", back_populates="snapshots")

    def __repr__(self):
        return f"<EnrollmentSnapshot {self.section_id} @ {self.timestamp}>"


class Notification(Base):
    """Notification record"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    monitor_id = Column(Integer, ForeignKey("course_monitors.id", ondelete="CASCADE"), nullable=False)
    section_id = Column(String, nullable=False)
    notification_type = Column(String, nullable=False)
    message = Column(Text, nullable=True)
    sent_at = Column(DateTime, server_default=func.now())
    success = Column(Boolean, default=True)

    # Relationships
    monitor = relationship("CourseMonitor", back_populates="notifications")

    def __repr__(self):
        return f"<Notification {self.notification_type} @ {self.sent_at}>"
