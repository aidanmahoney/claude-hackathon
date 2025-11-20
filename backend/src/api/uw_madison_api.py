"""UW Madison Course Search API Client using uwcourses.com"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import httpx

from src.config import settings
from src.utils.logger import logger


class UWMadisonAPI:
    """Client for UW Courses API - uses https://static.uwcourses.com/update.json"""

    def __init__(self):
        self.base_url = settings.api_base_url
        self.update_endpoint = settings.api_update_endpoint
        self.timeout = settings.request_timeout
        self.max_requests = settings.rate_limit_requests
        self.window_size = settings.rate_limit_window
        self.request_window: List[float] = []
        self.courses_cache: Optional[Dict[str, Any]] = None
        self.cache_timestamp: Optional[float] = None
        self.cache_ttl = 60  # Cache for 60 seconds

        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            headers={
                "Accept": "application/json",
                "User-Agent": "UW-Course-Checker/1.0"
            }
        )

    async def _check_rate_limit(self):
        """Check and enforce rate limiting"""
        now = time.time()
        self.request_window = [t for t in self.request_window if now - t < self.window_size]

        if len(self.request_window) >= self.max_requests:
            oldest_request = self.request_window[0]
            wait_time = self.window_size - (now - oldest_request)
            logger.warning(f"Rate limit approaching. Waiting {wait_time:.2f}s...")
            await asyncio.sleep(wait_time)

        self.request_window.append(now)

    async def _fetch_courses_data(self) -> Dict[str, Any]:
        """Fetch and cache courses data from uwcourses.com API"""
        now = time.time()

        # Return cached data if still valid
        if (self.courses_cache is not None and
            self.cache_timestamp is not None and
            now - self.cache_timestamp < self.cache_ttl):
            return self.courses_cache

        try:
            await self._check_rate_limit()

            logger.debug("Fetching courses data from uwcourses.com API")

            url = f"{self.base_url}{self.update_endpoint}"
            response = await self.client.get(url)
            response.raise_for_status()

            data = response.json()

            # Cache the response
            self.courses_cache = data
            self.cache_timestamp = now

            logger.info(f"Fetched course data with {len(data)} keys")
            return data

        except Exception as e:
            logger.error(f"Error fetching courses data: {e}")
            raise

    async def get_enrollment_status(
        self,
        term: str,
        subject: str,
        course_number: str
    ) -> Dict[str, Any]:
        """
        Get enrollment status for a course

        Args:
            term: Term code (e.g., "1252")
            subject: Subject code (e.g., "COMP SCI")
            course_number: Course number (e.g., "400")

        Returns:
            Dictionary containing enrollment data
        """
        try:
            logger.debug(f"Fetching enrollment for {subject} {course_number} (Term: {term})")

            # Fetch all courses data
            data = await self._fetch_courses_data()

            # Search for the specific course
            course_data = self._find_course(data, term, subject, course_number)

            if not course_data:
                raise ValueError(f"Course {subject} {course_number} not found for term {term}")

            return self._parse_enrollment_data(course_data, term, subject, course_number)

        except Exception as e:
            logger.error(f"Error fetching enrollment status: {e}")
            raise

    def _find_course(
        self,
        data: Dict[str, Any],
        term: str,
        subject: str,
        course_number: str
    ) -> Optional[Dict[str, Any]]:
        """Find a specific course in the API data"""
        # The uwcourses.com API structure may vary
        # Try multiple lookup strategies

        # Strategy 1: Check if data has a courses array
        if "courses" in data:
            for course in data["courses"]:
                if (course.get("subject") == subject and
                    str(course.get("catalogNumber", course.get("number", ""))) == str(course_number) and
                    str(course.get("term", "")) == str(term)):
                    return course

        # Strategy 2: Direct lookup by key variations
        for key_format in [
            f"{subject}{course_number}",
            f"{subject} {course_number}",
            f"{subject.replace(' ', '')}{course_number}",
            f"{term}:{subject}:{course_number}"
        ]:
            if key_format in data:
                return data[key_format]

        # Strategy 3: Iterate through all keys looking for matches
        for key, value in data.items():
            if isinstance(value, dict):
                if (value.get("subject") == subject and
                    str(value.get("catalogNumber", value.get("number", ""))) == str(course_number)):
                    return value

        return None

    def _parse_enrollment_data(
        self,
        course_data: Dict[str, Any],
        term: str,
        subject: str,
        course_number: str
    ) -> Dict[str, Any]:
        """Parse enrollment data from API response"""
        sections = course_data.get("sections", [])

        return {
            "term": term,
            "subject": subject,
            "courseNumber": course_number,
            "courseTitle": course_data.get("title", course_data.get("name", f"{subject} {course_number}")),
            "sections": [self._parse_section(section) for section in sections]
        }

    def _parse_section(self, section: Dict[str, Any]) -> Dict[str, Any]:
        """Parse section data with flexible field names"""
        # Support multiple field name variations
        enrollment_capacity = section.get("enrollmentCapacity", section.get("max_enrollment", section.get("capacity", 0)))
        enrollment_total = section.get("enrollmentTotal", section.get("current_enrollment", section.get("enrolled", 0)))
        waitlist_capacity = section.get("waitlistCapacity", section.get("max_waitlist", 0))
        waitlist_total = section.get("waitlistTotal", section.get("current_waitlist", section.get("waitlist", 0)))

        open_seats = max(0, enrollment_capacity - enrollment_total)
        waitlist_open = max(0, waitlist_capacity - waitlist_total)

        # Parse instructor information
        instructors = section.get("instructors", section.get("instructor", []))
        if isinstance(instructors, str):
            instructor_names = instructors
        elif isinstance(instructors, list):
            instructor_names = ", ".join([
                i.get("name", i) if isinstance(i, dict) else str(i)
                for i in instructors
            ]) or "TBA"
        else:
            instructor_names = "TBA"

        # Parse section identifier
        section_id = section.get("number", section.get("section", section.get("sectionNumber", "Unknown")))

        return {
            "sectionId": str(section_id),
            "classNumber": section.get("classNumber", section.get("class_number", section_id)),
            "instructor": instructor_names,
            "schedule": section.get("schedules", section.get("schedule", [])),
            "totalSeats": enrollment_capacity,
            "enrolledSeats": enrollment_total,
            "openSeats": open_seats,
            "waitlistTotal": waitlist_capacity,
            "waitlistEnrolled": waitlist_total,
            "waitlistOpen": waitlist_open,
            "status": self._determine_status(open_seats, waitlist_open),
            "lastUpdated": datetime.now().isoformat()
        }

    @staticmethod
    def _determine_status(open_seats: int, waitlist_open: int) -> str:
        """Determine enrollment status"""
        if open_seats > 0:
            return "OPEN"
        elif waitlist_open > 0:
            return "WAITLIST"
        else:
            return "CLOSED"

    async def get_current_term(self) -> str:
        """Get current term code from API data"""
        try:
            data = await self._fetch_courses_data()

            # Try to extract term from the data
            if "term" in data:
                return str(data["term"])

            if "current_term" in data:
                return str(data["current_term"])

            # If courses array exists, get term from first course
            if "courses" in data and len(data["courses"]) > 0:
                return str(data["courses"][0].get("term", "1252"))

            # Fallback to Spring 2025
            return "1252"

        except Exception as e:
            logger.error(f"Error fetching current term: {e}")
            return "1252"

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
