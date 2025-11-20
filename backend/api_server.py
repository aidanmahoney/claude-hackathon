"""FastAPI server for UW Course Checker"""

from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.services.course_checker import CourseChecker
from src.config import settings


# ==========================================
# Pydantic Models for API
# ==========================================

class CourseSectionResponse(BaseModel):
    sectionId: str
    classNumber: str
    totalSeats: int
    openSeats: int
    enrolledSeats: int
    waitlistTotal: int
    waitlistOpen: int
    status: str
    instructor: Optional[str] = None
    schedule: Optional[str] = None
    location: Optional[str] = None
    lastUpdated: str


class CourseResponse(BaseModel):
    id: str
    term: str
    subject: str
    courseNumber: str
    title: str
    credits: Optional[int] = None
    sections: List[CourseSectionResponse]


class MonitoredCourseRequest(BaseModel):
    term: str
    subject: str
    courseNumber: str
    sections: List[str] = []
    notifyOnOpen: bool = True
    notifyOnWaitlist: bool = False
    checkInterval: int = 300000  # milliseconds
    active: bool = True


class MonitoredCourseResponse(BaseModel):
    id: str
    term: str
    subject: str
    courseNumber: str
    sections: List[str]
    notifyOnOpen: bool
    notifyOnWaitlist: bool
    checkInterval: int
    active: bool
    lastChecked: Optional[datetime] = None
    createdAt: datetime


class EnrollmentSnapshotResponse(BaseModel):
    id: int
    courseMonitorId: int
    totalSeats: int
    openSeats: int
    enrolledSeats: int
    waitlistTotal: int
    waitlistOpen: int
    status: str
    timestamp: datetime


class NotificationPreferences(BaseModel):
    email: Optional[dict] = None
    sms: Optional[dict] = None
    webhook: Optional[dict] = None


class TestNotificationResponse(BaseModel):
    success: bool
    message: str


# ==========================================
# FastAPI Application with Lifespan
# ==========================================

# Global course checker instance
course_checker: CourseChecker


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    # Startup
    global course_checker
    course_checker = CourseChecker()
    await course_checker.initialize()

    yield

    # Shutdown
    await course_checker.cleanup()


app = FastAPI(
    title="UW Course Checker API",
    description="API for monitoring UW Madison course enrollment",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# API Endpoints
# ==========================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/api/courses/search", response_model=List[CourseResponse])
async def search_courses(
    term: str = Query(..., description="Term code (e.g., 1252)"),
    subject: Optional[str] = Query(None, description="Subject code (e.g., COMP SCI)"),
    courseNumber: Optional[str] = Query(None, description="Course number (e.g., 400)")
):
    """
    Search for courses

    NOTE: Currently only supports specific course lookup, not full search.
    The subject and courseNumber must be provided to get results.
    """
    if not subject or not courseNumber:
        return []

    try:
        enrollment_data = await course_checker.check_once(term, subject, courseNumber)

        return [_convert_to_course_response(enrollment_data)]

    except Exception as e:
        # Course not found or error - return empty list for search
        return []


@app.get("/api/courses/{term}/{subject}/{courseNumber}", response_model=CourseResponse)
async def get_course_details(term: str, subject: str, courseNumber: str):
    """Get detailed information for a specific course"""
    try:
        enrollment_data = await course_checker.check_once(term, subject, courseNumber)
        return _convert_to_course_response(enrollment_data)

    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Course not found: {str(e)}")


@app.get("/api/monitors", response_model=List[MonitoredCourseResponse])
async def get_monitored_courses():
    """Get all monitored courses"""
    monitors = course_checker.database.get_active_course_monitors()

    return [
        MonitoredCourseResponse(
            id=str(monitor.id),
            term=monitor.term,
            subject=monitor.subject,
            courseNumber=monitor.course_number,
            sections=[monitor.section_id] if monitor.section_id else [],
            notifyOnOpen=monitor.notify_on_open,
            notifyOnWaitlist=monitor.notify_on_waitlist,
            checkInterval=monitor.check_interval * 1000,  # Convert seconds to milliseconds
            active=monitor.active,
            lastChecked=monitor.last_checked,
            createdAt=monitor.created_at
        )
        for monitor in monitors
    ]


@app.post("/api/monitors", response_model=MonitoredCourseResponse)
async def add_monitored_course(course: MonitoredCourseRequest):
    """Add a new course to monitor"""
    try:
        # Convert milliseconds to seconds for backend
        check_interval_seconds = course.checkInterval // 1000

        # Get first section if specified, otherwise None
        section_id = course.sections[0] if course.sections else None

        monitor_id = await course_checker.add_course(
            term=course.term,
            subject=course.subject,
            course_number=course.courseNumber,
            section_id=section_id,
            notify_on_open=course.notifyOnOpen,
            notify_on_waitlist=course.notifyOnWaitlist,
            check_interval=check_interval_seconds
        )

        # Get the created monitor
        monitor = course_checker.database.get_course_monitor(monitor_id)

        return MonitoredCourseResponse(
            id=str(monitor.id),
            term=monitor.term,
            subject=monitor.subject,
            courseNumber=monitor.course_number,
            sections=[monitor.section_id] if monitor.section_id else [],
            notifyOnOpen=monitor.notify_on_open,
            notifyOnWaitlist=monitor.notify_on_waitlist,
            checkInterval=monitor.check_interval * 1000,
            active=monitor.active,
            lastChecked=monitor.last_checked,
            createdAt=monitor.created_at
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.patch("/api/monitors/{monitor_id}", response_model=MonitoredCourseResponse)
async def update_monitored_course(monitor_id: str, updates: dict):
    """Update a monitored course"""
    try:
        # Convert monitor_id to int
        monitor_id_int = int(monitor_id)

        # Get current monitor
        monitor = course_checker.database.get_course_monitor(monitor_id_int)
        if not monitor:
            raise HTTPException(status_code=404, detail="Monitor not found")

        # Update fields if provided
        if "active" in updates:
            if updates["active"]:
                course_checker.database.reactivate_course_monitor(monitor_id_int)
            else:
                course_checker.database.deactivate_course_monitor(monitor_id_int)

        # Refresh monitor data
        monitor = course_checker.database.get_course_monitor(monitor_id_int)

        return MonitoredCourseResponse(
            id=str(monitor.id),
            term=monitor.term,
            subject=monitor.subject,
            courseNumber=monitor.course_number,
            sections=[monitor.section_id] if monitor.section_id else [],
            notifyOnOpen=monitor.notify_on_open,
            notifyOnWaitlist=monitor.notify_on_waitlist,
            checkInterval=monitor.check_interval * 1000,
            active=monitor.active,
            lastChecked=monitor.last_checked,
            createdAt=monitor.created_at
        )

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid monitor ID")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/monitors/{monitor_id}")
async def remove_monitored_course(monitor_id: str):
    """Remove a monitored course"""
    try:
        monitor_id_int = int(monitor_id)
        await course_checker.remove_course(monitor_id_int)
        return {"success": True, "message": "Monitor removed successfully"}

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid monitor ID")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/monitors/{monitor_id}/history", response_model=List[EnrollmentSnapshotResponse])
async def get_enrollment_history(monitor_id: str, limit: int = Query(100, le=1000)):
    """Get enrollment history for a monitored course"""
    try:
        monitor_id_int = int(monitor_id)

        # Get monitor to extract subject and course number
        monitor = course_checker.database.get_course_monitor(monitor_id_int)
        if not monitor:
            raise HTTPException(status_code=404, detail="Monitor not found")

        history = course_checker.get_history(
            monitor.subject,
            monitor.course_number,
            limit=limit
        )

        return [
            EnrollmentSnapshotResponse(
                id=record.id,
                courseMonitorId=record.monitor_id,
                totalSeats=record.total_seats,
                openSeats=record.open_seats,
                enrolledSeats=record.enrolled_seats,
                waitlistTotal=record.waitlist_total,
                waitlistOpen=record.waitlist_open,
                status=record.status,
                timestamp=record.timestamp
            )
            for record in history
        ]

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid monitor ID")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/preferences/notifications", response_model=NotificationPreferences)
async def get_notification_preferences():
    """Get notification preferences"""
    return NotificationPreferences(
        email={
            "enabled": settings.email_enabled,
            "address": settings.email_to or ""
        },
        sms={
            "enabled": settings.sms_enabled,
            "phoneNumber": settings.twilio_phone_to or ""
        },
        webhook={
            "enabled": settings.webhook_enabled,
            "url": settings.webhook_url or ""
        }
    )


@app.put("/api/preferences/notifications", response_model=NotificationPreferences)
async def update_notification_preferences(preferences: NotificationPreferences):
    """
    Update notification preferences

    NOTE: This currently only returns the preferences.
    To persist changes, update the .env file manually.
    """
    # In a production app, you would save these to a database
    # For now, we just return what was sent
    return preferences


@app.post("/api/notifications/test", response_model=TestNotificationResponse)
async def test_notification(request: dict):
    """Test notification system"""
    notification_type = request.get("type", "email")

    try:
        await course_checker.notification_service.test_notifications()
        return TestNotificationResponse(
            success=True,
            message=f"Test notification sent via {notification_type}"
        )
    except Exception as e:
        return TestNotificationResponse(
            success=False,
            message=f"Failed to send test notification: {str(e)}"
        )


# ==========================================
# Helper Functions
# ==========================================

def _convert_to_course_response(enrollment_data: dict) -> CourseResponse:
    """Convert backend enrollment data to frontend course format"""

    # Generate a unique ID for the course
    course_id = f"{enrollment_data['subject']}-{enrollment_data['courseNumber']}-{enrollment_data['term']}"

    sections = [
        CourseSectionResponse(
            sectionId=section['sectionId'],
            classNumber=section['classNumber'],
            totalSeats=section['totalSeats'],
            openSeats=section['openSeats'],
            enrolledSeats=section['enrolledSeats'],
            waitlistTotal=section.get('waitlistTotal', 0),
            waitlistOpen=section.get('waitlistOpen', 0),
            status=section['status'],
            instructor=section.get('instructor'),
            schedule=None,  # Not provided by current API
            location=None,  # Not provided by current API
            lastUpdated=section.get('lastUpdated', datetime.now().isoformat())
        )
        for section in enrollment_data.get('sections', [])
    ]

    return CourseResponse(
        id=course_id,
        term=enrollment_data['term'],
        subject=enrollment_data['subject'],
        courseNumber=enrollment_data['courseNumber'],
        title=enrollment_data.get('courseTitle', ''),
        credits=None,  # Not provided by current API
        sections=sections
    )


# ==========================================
# Main Entry Point
# ==========================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=3000,
        reload=True,
        log_level="info"
    )
