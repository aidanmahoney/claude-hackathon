"""Notification service for sending alerts"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List
import httpx

from src.config import settings
from src.utils.logger import logger


class NotificationService:
    """Service for sending notifications via email, SMS, and webhooks"""

    def __init__(self):
        self.settings = settings

    async def notify_course_available(self, course_data: Dict[str, Any]):
        """Send notifications when a course becomes available"""
        notifications = []

        if self.settings.email_enabled and self.settings.email_smtp_user:
            try:
                await self._send_email(course_data)
                notifications.append("email")
            except Exception as e:
                logger.error(f"Failed to send email: {e}")

        if self.settings.sms_enabled and self.settings.twilio_account_sid:
            try:
                await self._send_sms(course_data)
                notifications.append("sms")
            except Exception as e:
                logger.error(f"Failed to send SMS: {e}")

        if self.settings.webhook_enabled and self.settings.webhook_url:
            try:
                await self._send_webhook(course_data)
                notifications.append("webhook")
            except Exception as e:
                logger.error(f"Failed to send webhook: {e}")

        logger.info(
            f"Notifications sent for {course_data['subject']} {course_data['courseNumber']}: "
            f"{', '.join(notifications) if notifications else 'none'}"
        )

    async def _send_email(self, course_data: Dict[str, Any]):
        """Send email notification"""
        if not all([
            self.settings.email_smtp_user,
            self.settings.email_smtp_pass,
            self.settings.email_from,
            self.settings.email_to
        ]):
            logger.warning("Email not configured properly")
            return

        subject = f"Course Available: {course_data['subject']} {course_data['courseNumber']}"
        html_content = self._generate_email_html(course_data)

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.settings.email_from
        message["To"] = self.settings.email_to

        html_part = MIMEText(html_content, "html")
        message.attach(html_part)

        with smtplib.SMTP(self.settings.email_smtp_host, self.settings.email_smtp_port) as server:
            server.starttls()
            server.login(self.settings.email_smtp_user, self.settings.email_smtp_pass)
            server.send_message(message)

        logger.info(f"Email sent for {course_data['subject']} {course_data['courseNumber']}")

    def _generate_email_html(self, course_data: Dict[str, Any]) -> str:
        """Generate HTML email template"""
        open_sections = [s for s in course_data["sections"] if s["status"] == "OPEN"]
        waitlist_sections = [s for s in course_data["sections"] if s["status"] == "WAITLIST"]

        sections_html = ""

        if open_sections:
            sections_html += '<h3 style="color: #28a745;">Open Sections:</h3><ul>'
            for section in open_sections:
                sections_html += f"""
                <li>
                    <strong>Section {section['sectionId']}</strong> (Class #{section['classNumber']})<br>
                    Instructor: {section['instructor']}<br>
                    Open Seats: <strong style="color: #28a745;">{section['openSeats']}/{section['totalSeats']}</strong><br>
                </li>
                """
            sections_html += "</ul>"

        if waitlist_sections:
            sections_html += '<h3 style="color: #ffc107;">Waitlist Available:</h3><ul>'
            for section in waitlist_sections:
                sections_html += f"""
                <li>
                    <strong>Section {section['sectionId']}</strong> (Class #{section['classNumber']})<br>
                    Instructor: {section['instructor']}<br>
                    Waitlist: <strong style="color: #ffc107;">{section['waitlistOpen']}/{section['waitlistTotal']} open</strong><br>
                </li>
                """
            sections_html += "</ul>"

        return f"""
<!DOCTYPE html>
<html>
  <head>
    <style>
      body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
      .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
      .header {{ background-color: #c5050c; color: white; padding: 20px; text-align: center; }}
      .content {{ padding: 20px; background-color: #f9f9f9; }}
      .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
      ul {{ padding-left: 20px; }}
      li {{ margin-bottom: 15px; }}
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <h1>Course Now Available!</h1>
      </div>
      <div class="content">
        <h2>{course_data['subject']} {course_data['courseNumber']}: {course_data['courseTitle']}</h2>
        <p><strong>Term:</strong> {course_data['term']}</p>
        {sections_html}
        <p style="margin-top: 30px;">
          <a href="https://enroll.wisc.edu"
             style="background-color: #c5050c; color: white; padding: 12px 24px;
                    text-decoration: none; border-radius: 4px; display: inline-block;">
            Enroll Now
          </a>
        </p>
      </div>
      <div class="footer">
        <p>This notification was sent by UW Course Checker</p>
      </div>
    </div>
  </body>
</html>
"""

    async def _send_sms(self, course_data: Dict[str, Any]):
        """Send SMS notification"""
        try:
            from twilio.rest import Client

            client = Client(
                self.settings.twilio_account_sid,
                self.settings.twilio_auth_token
            )

            open_sections = [s for s in course_data["sections"] if s["status"] == "OPEN"]

            if open_sections:
                message = (
                    f"Course OPEN: {course_data['subject']} {course_data['courseNumber']} - "
                    f"Section(s) {', '.join(s['sectionId'] for s in open_sections)}. "
                    f"Enroll now at enroll.wisc.edu"
                )
            else:
                message = (
                    f"Waitlist available: {course_data['subject']} {course_data['courseNumber']}. "
                    f"Check enroll.wisc.edu"
                )

            client.messages.create(
                body=message,
                from_=self.settings.twilio_phone_from,
                to=self.settings.twilio_phone_to
            )

            logger.info(f"SMS sent for {course_data['subject']} {course_data['courseNumber']}")

        except ImportError:
            logger.error("Twilio not installed. Install with: pip install twilio")
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            raise

    async def _send_webhook(self, course_data: Dict[str, Any]):
        """Send webhook notification"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.settings.webhook_url,
                json={
                    "event": "course_available",
                    "timestamp": course_data["sections"][0]["lastUpdated"],
                    "data": course_data
                }
            )
            response.raise_for_status()

        logger.info(f"Webhook sent for {course_data['subject']} {course_data['courseNumber']}")

    async def test_notifications(self):
        """Test notification system"""
        test_data = {
            "term": "1252",
            "subject": "COMP SCI",
            "courseNumber": "400",
            "courseTitle": "Programming III",
            "sections": [{
                "sectionId": "001",
                "classNumber": "12345",
                "instructor": "Test Instructor",
                "schedule": [],
                "totalSeats": 30,
                "enrolledSeats": 29,
                "openSeats": 1,
                "waitlistTotal": 10,
                "waitlistEnrolled": 5,
                "waitlistOpen": 5,
                "status": "OPEN",
                "lastUpdated": "2025-01-01T00:00:00"
            }]
        }

        logger.info("Sending test notification...")
        await self.notify_course_available(test_data)
        logger.info("Test notification completed")
