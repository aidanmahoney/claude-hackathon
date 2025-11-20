"""Course checker service for monitoring course availability"""

import asyncio
from typing import Dict, Any, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.api.uw_madison_api import UWMadisonAPI
from src.services.notification_service import NotificationService
from src.database.database import Database
from src.database.models import CourseMonitor
from src.utils.logger import logger


class CourseChecker:
    """Service for monitoring course enrollment status"""

    def __init__(self):
        self.api = UWMadisonAPI()
        self.notification_service = NotificationService()
        self.database = Database()
        self.scheduler = AsyncIOScheduler()
        self.is_running = False

    async def initialize(self):
        """Initialize the course checker"""
        self.database.initialize()
        logger.info("CourseChecker initialized")

    async def start(self):
        """Start monitoring all active courses"""
        if self.is_running:
            logger.warning("CourseChecker is already running")
            return

        self.is_running = True
        logger.info("Starting course monitoring...")

        active_monitors = self.database.get_active_course_monitors()

        if not active_monitors:
            logger.warning("No active course monitors found. Add courses using the CLI.")
            return

        for monitor in active_monitors:
            await self.setup_monitor(monitor)

        self.scheduler.start()
        logger.info(f"Monitoring {len(active_monitors)} course(s)")

    async def setup_monitor(self, monitor: CourseMonitor):
        """Set up monitoring for a specific course"""
        self.scheduler.add_job(
            self.check_course,
            trigger=IntervalTrigger(seconds=monitor.check_interval),
            args=[monitor],
            id=f"monitor_{monitor.id}",
            replace_existing=True
        )

        await self.check_course(monitor)

        logger.info(
            f"Monitor setup for {monitor.subject} {monitor.course_number} "
            f"(every {monitor.check_interval}s)"
        )

    async def check_course(self, monitor: CourseMonitor):
        """Check a specific course for availability"""
        try:
            logger.debug(f"Checking {monitor.subject} {monitor.course_number}...")

            enrollment_data = await self.api.get_enrollment_status(
                monitor.term,
                monitor.subject,
                monitor.course_number
            )

            self.database.update_last_checked(monitor.id)

            for section in enrollment_data["sections"]:
                if monitor.section_id and section["sectionId"] != monitor.section_id:
                    continue

                await self.process_section(monitor, section, enrollment_data)

        except Exception as e:
            logger.error(
                f"Error checking course {monitor.subject} {monitor.course_number}: {e}"
            )

    async def process_section(
        self,
        monitor: CourseMonitor,
        current_section: Dict[str, Any],
        course_data: Dict[str, Any]
    ):
        """Process a section and detect changes"""
        previous_snapshot = self.database.get_latest_snapshot(
            monitor.id,
            current_section["sectionId"]
        )

        self.database.save_enrollment_snapshot(
            monitor_id=monitor.id,
            section_id=current_section["sectionId"],
            class_number=current_section["classNumber"],
            total_seats=current_section["totalSeats"],
            enrolled_seats=current_section["enrolledSeats"],
            open_seats=current_section["openSeats"],
            waitlist_total=current_section["waitlistTotal"],
            waitlist_enrolled=current_section["waitlistEnrolled"],
            waitlist_open=current_section["waitlistOpen"],
            status=current_section["status"],
            instructor=current_section["instructor"]
        )

        if previous_snapshot:
            await self.detect_changes(monitor, previous_snapshot, current_section, course_data)
        else:
            logger.info(
                f"First snapshot for {monitor.subject} {monitor.course_number} "
                f"Section {current_section['sectionId']}"
            )

    async def detect_changes(
        self,
        monitor: CourseMonitor,
        previous: Any,
        current: Dict[str, Any],
        course_data: Dict[str, Any]
    ):
        """Detect enrollment changes and trigger notifications"""
        changes = []

        if previous.status != current["status"]:
            changes.append({
                "type": "status",
                "from": previous.status,
                "to": current["status"]
            })

        if previous.open_seats < current["openSeats"] and current["openSeats"] > 0:
            changes.append({
                "type": "seats_opened",
                "previous": previous.open_seats,
                "current": current["openSeats"]
            })

        if previous.waitlist_open < current["waitlistOpen"] and current["waitlistOpen"] > 0:
            changes.append({
                "type": "waitlist_opened",
                "previous": previous.waitlist_open,
                "current": current["waitlistOpen"]
            })

        for change in changes:
            await self.handle_change(monitor, current, course_data, change)

    async def handle_change(
        self,
        monitor: CourseMonitor,
        section: Dict[str, Any],
        course_data: Dict[str, Any],
        change: Dict[str, Any]
    ):
        """Handle detected change and send notifications"""
        logger.info(
            f"Change detected: {change['type']} for {monitor.subject} {monitor.course_number} "
            f"Section {section['sectionId']}"
        )

        should_notify = False

        if change["type"] == "status" and change["to"] == "OPEN" and monitor.notify_on_open:
            should_notify = True
        elif change["type"] == "seats_opened" and monitor.notify_on_open:
            should_notify = True
        elif change["type"] == "waitlist_opened" and monitor.notify_on_waitlist:
            should_notify = True

        if should_notify:
            try:
                await self.notification_service.notify_course_available({
                    **course_data,
                    "sections": [section]
                })

                self.database.save_notification(
                    monitor_id=monitor.id,
                    section_id=section["sectionId"],
                    notification_type=change["type"],
                    message=f"{change['type']}: {change}",
                    success=True
                )

            except Exception as e:
                logger.error(f"Failed to send notification: {e}")
                self.database.save_notification(
                    monitor_id=monitor.id,
                    section_id=section["sectionId"],
                    notification_type=change["type"],
                    message=str(e),
                    success=False
                )

    async def add_course(
        self,
        term: str,
        subject: str,
        course_number: str,
        section_id: Optional[str] = None,
        notify_on_open: bool = True,
        notify_on_waitlist: bool = False,
        check_interval: int = 300
    ) -> int:
        """Add a new course to monitor"""
        monitor_id = self.database.add_course_monitor(
            term=term,
            subject=subject,
            course_number=course_number,
            section_id=section_id,
            notify_on_open=notify_on_open,
            notify_on_waitlist=notify_on_waitlist,
            check_interval=check_interval
        )

        if self.is_running:
            monitor = self.database.get_course_monitor(monitor_id)
            if monitor:
                await self.setup_monitor(monitor)

        return monitor_id

    async def remove_course(self, monitor_id: int):
        """Remove course from monitoring"""
        try:
            self.scheduler.remove_job(f"monitor_{monitor_id}")
        except Exception:
            pass

        self.database.deactivate_course_monitor(monitor_id)
        logger.info(f"Course monitor {monitor_id} removed")

    async def check_once(
        self,
        term: str,
        subject: str,
        course_number: str
    ) -> Dict[str, Any]:
        """Check a course once (manual check)"""
        logger.info(f"Manual check for {subject} {course_number} (Term: {term})")
        enrollment_data = await self.api.get_enrollment_status(term, subject, course_number)
        return enrollment_data

    def get_history(
        self,
        subject: str,
        course_number: str,
        limit: int = 100
    ):
        """Get enrollment history for a course"""
        return self.database.get_enrollment_history(subject, course_number, limit)

    async def stop(self):
        """Stop monitoring all courses"""
        if not self.is_running:
            return

        logger.info("Stopping course monitoring...")

        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

        self.is_running = False
        logger.info("Course monitoring stopped")

    async def cleanup(self):
        """Clean up resources"""
        await self.stop()
        await self.api.close()
        self.database.close()
        logger.info("CourseChecker cleanup complete")
