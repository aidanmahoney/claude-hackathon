"""UW Madison Course Search and Enroll API Client"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import httpx

from src.config import settings
from src.utils.logger import logger


class UWMadisonAPI:
    """Client for UW Madison Course Search and Enroll API"""

    def __init__(self):
        self.base_url = settings.api_base_url
        self.timeout = settings.request_timeout
        self.max_requests = settings.rate_limit_requests
        self.window_size = settings.rate_limit_window
        self.request_window: List[float] = []

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
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
            await self._check_rate_limit()

            logger.debug(f"Fetching enrollment for {subject} {course_number} (Term: {term})")

            response = await self.client.get(
                "/search/v1/courses",
                params={
                    "term": term,
                    "subject": subject,
                    "catalogNumber": course_number
                }
            )
            response.raise_for_status()

            data = response.json()
            return self._parse_enrollment_data(data)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                retry_after = int(e.response.headers.get("retry-after", 60))
                logger.warning(f"Rate limited. Waiting {retry_after}s...")
                await asyncio.sleep(retry_after)
                return await self.get_enrollment_status(term, subject, course_number)
            raise
        except Exception as e:
            logger.error(f"Error fetching enrollment status: {e}")
            raise

    async def get_section_details(self, term: str, section_id: str) -> Dict[str, Any]:
        """
        Get details for a specific section

        Args:
            term: Term code
            section_id: Section ID

        Returns:
            Dictionary containing section data
        """
        try:
            await self._check_rate_limit()

            logger.debug(f"Fetching section details for {section_id} (Term: {term})")

            response = await self.client.get(f"/search/v1/sections/{term}/{section_id}")
            response.raise_for_status()

            return response.json()

        except Exception as e:
            logger.error(f"Error fetching section details: {e}")
            raise

    async def search_courses(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search for courses

        Args:
            params: Search parameters

        Returns:
            List of courses
        """
        try:
            await self._check_rate_limit()

            logger.debug(f"Searching courses with params: {params}")

            response = await self.client.get("/search/v1/courses", params=params)
            response.raise_for_status()

            return response.json()

        except Exception as e:
            logger.error(f"Error searching courses: {e}")
            raise

    def _parse_enrollment_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse enrollment data from API response

        Args:
            data: Raw API response

        Returns:
            Parsed enrollment data
        """
        if not data or "courses" not in data or len(data["courses"]) == 0:
            raise ValueError("No course data found")

        course = data["courses"][0]
        sections = course.get("sections", [])

        return {
            "term": course.get("term"),
            "subject": course.get("subject"),
            "courseNumber": course.get("catalogNumber"),
            "courseTitle": course.get("title"),
            "sections": [self._parse_section(section) for section in sections]
        }

    def _parse_section(self, section: Dict[str, Any]) -> Dict[str, Any]:
        """Parse section data"""
        enrollment_capacity = section.get("enrollmentCapacity", 0)
        enrollment_total = section.get("enrollmentTotal", 0)
        waitlist_capacity = section.get("waitlistCapacity", 0)
        waitlist_total = section.get("waitlistTotal", 0)

        open_seats = max(0, enrollment_capacity - enrollment_total)
        waitlist_open = max(0, waitlist_capacity - waitlist_total)

        instructors = section.get("instructors", [])
        instructor_names = ", ".join([i.get("name", "") for i in instructors]) or "TBA"

        return {
            "sectionId": section.get("number"),
            "classNumber": section.get("classNumber"),
            "instructor": instructor_names,
            "schedule": section.get("schedules", []),
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
        """
        Get current term code

        Returns:
            Current term code
        """
        try:
            response = await self.client.get("/search/v1/terms")
            response.raise_for_status()

            data = response.json()
            terms = data.get("terms", [])

            # Find current or next active term
            now = datetime.now()
            for term in terms:
                start_date = datetime.fromisoformat(term.get("startDate", ""))
                end_date = datetime.fromisoformat(term.get("endDate", ""))
                if start_date <= now <= end_date:
                    return term.get("code")

            # Fallback to first term
            return terms[0].get("code") if terms else "1252"

        except Exception as e:
            logger.error(f"Error fetching current term: {e}")
            return "1252"  # Fallback to Spring 2025

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
