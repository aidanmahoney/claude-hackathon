"""UW Madison Course Search API Client using uwcourses.com"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import httpx

from src.config import settings
from src.utils.logger import logger


class UWMadisonAPI:
    """Client for UW Courses API - uses https://static.uwcourses.com/course/{SUBJECT}_{NUMBER}.json"""

    def __init__(self):
        self.base_url = settings.api_base_url
        self.timeout = settings.request_timeout
        self.max_requests = settings.rate_limit_requests
        self.window_size = settings.rate_limit_window
        self.request_window: List[float] = []
        self.cache: Dict[str, Any] = {}  # Cache for individual courses
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

    async def _fetch_course_data(self, subject: str, course_number: str) -> Dict[str, Any]:
        """Fetch course data from uwcourses.com API"""
        # Normalize subject - remove spaces (e.g., "COMP SCI" -> "COMPSCI")
        normalized_subject = subject.replace(" ", "").upper()
        cache_key = f"{normalized_subject}_{course_number}"

        now = time.time()

        # Return cached data if still valid
        if cache_key in self.cache:
            cached_data, cache_time = self.cache[cache_key]
            if now - cache_time < self.cache_ttl:
                return cached_data

        try:
            await self._check_rate_limit()

            logger.debug(f"Fetching course data for {normalized_subject} {course_number}")

            url = f"{self.base_url}/course/{normalized_subject}_{course_number}.json"
            response = await self.client.get(url)
            response.raise_for_status()

            data = response.json()

            # Cache the response
            self.cache[cache_key] = (data, now)

            logger.info(f"Fetched course data for {normalized_subject} {course_number}")
            return data

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Course {subject} {course_number} not found")
            logger.error(f"Error fetching course data: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching course data: {e}")
            raise

    async def get_enrollment_status(
        self,
        term: str,
        subject: str,
        course_number: str
    ) -> Dict[str, Any]:
        """
        Get enrollment status for a course

        NOTE: The uwcourses.com API provides historical grade data and course metadata,
        but NOT real-time seat availability. This method generates mock enrollment data.

        Args:
            term: Term code (e.g., "1252")
            subject: Subject code (e.g., "COMP SCI")
            course_number: Course number (e.g., "400")

        Returns:
            Dictionary containing enrollment data
        """
        try:
            logger.debug(f"Fetching enrollment for {subject} {course_number} (Term: {term})")

            # Fetch course data from the API
            course_data = await self._fetch_course_data(subject, course_number)

            # Check if the term exists in the course data
            if term not in course_data.get("term_data", {}):
                logger.warning(f"Term {term} not found for {subject} {course_number}, using mock data")

            return self._parse_enrollment_data(course_data, term, subject, course_number)

        except Exception as e:
            logger.error(f"Error fetching enrollment status: {e}")
            raise


    def _parse_enrollment_data(
        self,
        course_data: Dict[str, Any],
        term: str,
        subject: str,
        course_number: str
    ) -> Dict[str, Any]:
        """Parse enrollment data from API response and generate mock sections"""
        course_title = course_data.get("course_title", f"{subject} {course_number}")

        # Get term-specific data if available
        term_data = course_data.get("term_data", {}).get(term, {})
        enrollment_data = term_data.get("enrollment_data", {})

        # Generate mock sections based on enrollment data or create default ones
        sections = []

        if enrollment_data and enrollment_data.get("instructors"):
            # Create a section for each instructor
            instructors = enrollment_data.get("instructors", {})
            for idx, (instructor_name, email) in enumerate(instructors.items(), start=1):
                section_id = f"{idx:03d}"
                sections.append(self._create_mock_section(section_id, instructor_name, idx))
        else:
            # Create default mock sections
            sections.append(self._create_mock_section("001", "TBA", 1))
            sections.append(self._create_mock_section("002", "TBA", 2))

        return {
            "term": term,
            "subject": subject,
            "courseNumber": course_number,
            "courseTitle": course_title,
            "sections": sections
        }

    def _create_mock_section(self, section_id: str, instructor: str, seed: int) -> Dict[str, Any]:
        """
        Create mock section data with randomized enrollment numbers

        NOTE: This is MOCK DATA because the uwcourses.com API doesn't provide real-time enrollment.
        For production use, you need to integrate with the official UW Madison enrollment API.
        """
        import random
        random.seed(seed + int(time.time()) % 100)  # Semi-random based on time

        # Generate realistic enrollment numbers
        total_seats = random.choice([30, 40, 50, 100, 150, 200])
        enrolled_seats = random.randint(int(total_seats * 0.7), total_seats)
        open_seats = max(0, total_seats - enrolled_seats)

        waitlist_total = random.choice([0, 10, 20, 30])
        waitlist_enrolled = random.randint(0, waitlist_total) if waitlist_total > 0 else 0
        waitlist_open = max(0, waitlist_total - waitlist_enrolled)

        status = self._determine_status(open_seats, waitlist_open)

        return {
            "sectionId": section_id,
            "classNumber": f"1{random.randint(1000, 9999)}",
            "instructor": instructor,
            "schedule": [],
            "totalSeats": total_seats,
            "enrolledSeats": enrolled_seats,
            "openSeats": open_seats,
            "waitlistTotal": waitlist_total,
            "waitlistEnrolled": waitlist_enrolled,
            "waitlistOpen": waitlist_open,
            "status": status,
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
        """Get current term code"""
        # The uwcourses.com API doesn't provide current term info
        # Default to Spring 2025 (term code 1252)
        # In production, this should be dynamically determined or configured
        return "1252"

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
