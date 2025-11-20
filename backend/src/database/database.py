"""Database connection and operations"""

from pathlib import Path
from typing import List, Optional
from datetime import datetime
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session

from src.config import settings
from src.database.models import Base, CourseMonitor, EnrollmentSnapshot, Notification
from src.utils.logger import logger


class Database:
    """Database connection and operations manager"""

    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or settings.database_url

        # Ensure data directory exists for SQLite
        if self.database_url.startswith("sqlite"):
            db_path = self.database_url.replace("sqlite:///", "")
            if db_path.startswith("./"):
                db_path = Path(__file__).parent.parent.parent / db_path[2:]
                db_path.parent.mkdir(parents=True, exist_ok=True)

        self.engine = create_engine(self.database_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def initialize(self):
        """Initialize database and create tables"""
        Base.metadata.create_all(self.engine)
        logger.info(f"Database initialized at {self.database_url}")

    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()

    def add_course_monitor(
        self,
        term: str,
        subject: str,
        course_number: str,
        section_id: Optional[str] = None,
        notify_on_open: bool = True,
        notify_on_waitlist: bool = False,
        check_interval: int = 300
    ) -> int:
        """Add a new course monitor"""
        with self.get_session() as session:
            # Check if monitor already exists (prevent duplicates)
            existing_stmt = select(CourseMonitor).where(
                CourseMonitor.term == term,
                CourseMonitor.subject == subject,
                CourseMonitor.course_number == course_number,
                CourseMonitor.section_id == section_id,
                CourseMonitor.active == True
            )
            existing = session.execute(existing_stmt).scalar_one_or_none()

            if existing:
                logger.warning(f"Monitor already exists for {subject} {course_number} (ID: {existing.id})")
                return existing.id

            monitor = CourseMonitor(
                term=term,
                subject=subject,
                course_number=course_number,
                section_id=section_id,
                notify_on_open=notify_on_open,
                notify_on_waitlist=notify_on_waitlist,
                check_interval=check_interval
            )
            session.add(monitor)
            session.commit()
            session.refresh(monitor)

            logger.info(f"Added course monitor: {subject} {course_number}")
            return monitor.id

    def get_active_course_monitors(self) -> List[CourseMonitor]:
        """Get all active course monitors"""
        with self.get_session() as session:
            stmt = select(CourseMonitor).where(CourseMonitor.active == True)
            result = session.execute(stmt)
            monitors = result.scalars().all()
            return [session.merge(m) for m in monitors]

    def get_course_monitor(self, monitor_id: int) -> Optional[CourseMonitor]:
        """Get specific course monitor by ID"""
        with self.get_session() as session:
            stmt = select(CourseMonitor).where(CourseMonitor.id == monitor_id)
            result = session.execute(stmt)
            monitor = result.scalar_one_or_none()
            if monitor:
                return session.merge(monitor)
            return None

    def update_last_checked(self, monitor_id: int):
        """Update last checked timestamp"""
        with self.get_session() as session:
            stmt = select(CourseMonitor).where(CourseMonitor.id == monitor_id)
            result = session.execute(stmt)
            monitor = result.scalar_one_or_none()
            if monitor:
                monitor.last_checked = datetime.now()
                session.commit()

    def save_enrollment_snapshot(
        self,
        monitor_id: int,
        section_id: str,
        class_number: Optional[str],
        total_seats: int,
        enrolled_seats: int,
        open_seats: int,
        waitlist_total: int,
        waitlist_enrolled: int,
        waitlist_open: int,
        status: str,
        instructor: str
    ) -> int:
        """Save an enrollment snapshot"""
        with self.get_session() as session:
            snapshot = EnrollmentSnapshot(
                monitor_id=monitor_id,
                section_id=section_id,
                class_number=class_number,
                total_seats=total_seats,
                enrolled_seats=enrolled_seats,
                open_seats=open_seats,
                waitlist_total=waitlist_total,
                waitlist_enrolled=waitlist_enrolled,
                waitlist_open=waitlist_open,
                status=status,
                instructor=instructor
            )
            session.add(snapshot)
            session.commit()
            session.refresh(snapshot)
            return snapshot.id

    def get_latest_snapshot(
        self,
        monitor_id: int,
        section_id: str
    ) -> Optional[EnrollmentSnapshot]:
        """Get the latest enrollment snapshot for a monitor and section"""
        with self.get_session() as session:
            stmt = (
                select(EnrollmentSnapshot)
                .where(
                    EnrollmentSnapshot.monitor_id == monitor_id,
                    EnrollmentSnapshot.section_id == section_id
                )
                .order_by(EnrollmentSnapshot.timestamp.desc())
                .limit(1)
            )
            result = session.execute(stmt)
            snapshot = result.scalar_one_or_none()
            if snapshot:
                return session.merge(snapshot)
            return None

    def get_enrollment_history(
        self,
        subject: str,
        course_number: str,
        limit: int = 100
    ) -> List[EnrollmentSnapshot]:
        """Get enrollment history for a course"""
        with self.get_session() as session:
            stmt = (
                select(EnrollmentSnapshot)
                .join(CourseMonitor)
                .where(
                    CourseMonitor.subject == subject,
                    CourseMonitor.course_number == course_number
                )
                .order_by(EnrollmentSnapshot.timestamp.desc())
                .limit(limit)
            )
            result = session.execute(stmt)
            snapshots = result.scalars().all()
            return [session.merge(s) for s in snapshots]

    def save_notification(
        self,
        monitor_id: int,
        section_id: str,
        notification_type: str,
        message: str,
        success: bool = True
    ) -> int:
        """Save a notification record"""
        with self.get_session() as session:
            notification = Notification(
                monitor_id=monitor_id,
                section_id=section_id,
                notification_type=notification_type,
                message=message,
                success=success
            )
            session.add(notification)
            session.commit()
            session.refresh(notification)
            return notification.id

    def deactivate_course_monitor(self, monitor_id: int):
        """Deactivate a course monitor"""
        with self.get_session() as session:
            stmt = select(CourseMonitor).where(CourseMonitor.id == monitor_id)
            result = session.execute(stmt)
            monitor = result.scalar_one_or_none()
            if monitor:
                monitor.active = False
                session.commit()
                logger.info(f"Deactivated course monitor: {monitor_id}")

    def reactivate_course_monitor(self, monitor_id: int):
        """Reactivate a course monitor"""
        with self.get_session() as session:
            stmt = select(CourseMonitor).where(CourseMonitor.id == monitor_id)
            result = session.execute(stmt)
            monitor = result.scalar_one_or_none()
            if monitor:
                monitor.active = True
                session.commit()
                logger.info(f"Reactivated course monitor: {monitor_id}")

    def delete_course_monitor(self, monitor_id: int):
        """Delete a course monitor"""
        with self.get_session() as session:
            stmt = select(CourseMonitor).where(CourseMonitor.id == monitor_id)
            result = session.execute(stmt)
            monitor = result.scalar_one_or_none()
            if monitor:
                session.delete(monitor)
                session.commit()
                logger.info(f"Deleted course monitor: {monitor_id}")

    def close(self):
        """Close database connection"""
        self.engine.dispose()
        logger.info("Database connection closed")
