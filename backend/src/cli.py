"""Command-line interface for UW Course Checker"""

import asyncio
import signal
import sys
import click
from datetime import datetime

from src.services.course_checker import CourseChecker
from src.utils.logger import logger


def get_status_icon(status: str) -> str:
    """Get icon for status"""
    icons = {
        "OPEN": "✅",
        "WAITLIST": "⚠️",
        "CLOSED": "❌"
    }
    return icons.get(status, "❓")


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """UW Madison course enrollment monitoring tool"""
    pass


@cli.command()
def monitor():
    """Start monitoring all active courses"""
    async def run_monitor():
        checker = CourseChecker()

        try:
            await checker.initialize()
            await checker.start()

            click.echo("\n🔍 Course monitoring started!")
            click.echo("Press Ctrl+C to stop\n")

            # Set up signal handlers
            def signal_handler(sig, frame):
                click.echo("\n\nStopping course monitoring...")
                asyncio.create_task(checker.cleanup())
                sys.exit(0)

            signal.signal(signal.SIGINT, signal_handler)

            # Keep running
            while True:
                await asyncio.sleep(1)

        except Exception as e:
            click.echo(f"Failed to start monitoring: {e}", err=True)
            sys.exit(1)

    asyncio.run(run_monitor())


@cli.command()
@click.option("-t", "--term", required=True, help="Term code (e.g., 1252)")
@click.option("-s", "--subject", required=True, help='Subject code (e.g., "COMP SCI")')
@click.option("-n", "--number", required=True, help="Course number (e.g., 400)")
def check(term: str, subject: str, number: str):
    """Check a specific course once"""
    async def run_check():
        checker = CourseChecker()

        try:
            await checker.initialize()

            click.echo(f"\nChecking {subject} {number} (Term: {term})...\n")

            enrollment_data = await checker.check_once(term, subject, number)

            # Display results
            click.echo(
                f"📚 {enrollment_data['subject']} {enrollment_data['courseNumber']}: "
                f"{enrollment_data['courseTitle']}"
            )
            click.echo(f"Term: {enrollment_data['term']}\n")

            for section in enrollment_data["sections"]:
                click.echo(f"Section {section['sectionId']} (Class #{section['classNumber']})")
                click.echo(f"  Instructor: {section['instructor']}")
                click.echo(f"  Status: {get_status_icon(section['status'])} {section['status']}")
                click.echo(f"  Seats: {section['openSeats']}/{section['totalSeats']} open")
                click.echo(f"  Waitlist: {section['waitlistOpen']}/{section['waitlistTotal']} open")
                click.echo("")

            await checker.cleanup()

        except Exception as e:
            click.echo(f"Failed to check course: {e}", err=True)
            sys.exit(1)

    asyncio.run(run_check())


@cli.command()
@click.option("-t", "--term", required=True, help="Term code (e.g., 1252)")
@click.option("-s", "--subject", required=True, help='Subject code (e.g., "COMP SCI")')
@click.option("-n", "--number", required=True, help="Course number (e.g., 400)")
@click.option("--section", help="Specific section to monitor (optional)")
@click.option("--notify-open/--no-notify-open", default=True, help="Notify when seats open")
@click.option("--notify-waitlist/--no-notify-waitlist", default=False, help="Notify when waitlist opens")
@click.option("-i", "--interval", type=int, default=300, help="Check interval in seconds")
def add(
    term: str,
    subject: str,
    number: str,
    section: str,
    notify_open: bool,
    notify_waitlist: bool,
    interval: int
):
    """Add a course to monitoring list"""
    async def run_add():
        checker = CourseChecker()

        try:
            await checker.initialize()

            monitor_id = await checker.add_course(
                term=term,
                subject=subject,
                course_number=number,
                section_id=section,
                notify_on_open=notify_open,
                notify_on_waitlist=notify_waitlist,
                check_interval=interval
            )

            click.echo(f"\n✓ Added course monitor (ID: {monitor_id})")
            click.echo(f"  {subject} {number} (Term: {term})")
            if section:
                click.echo(f"  Section: {section}")
            click.echo(f"  Check interval: {interval} seconds")
            click.echo(f"  Notify on open: {notify_open}")
            click.echo(f"  Notify on waitlist: {notify_waitlist}\n")

            await checker.cleanup()

        except Exception as e:
            click.echo(f"Failed to add course: {e}", err=True)
            sys.exit(1)

    asyncio.run(run_add())


@cli.command()
def list():
    """List all active course monitors"""
    async def run_list():
        checker = CourseChecker()

        try:
            await checker.initialize()

            monitors = checker.database.get_active_course_monitors()

            if not monitors:
                click.echo("\nNo active course monitors found.\n")
            else:
                click.echo(f"\n📋 Active Course Monitors ({len(monitors)}):\n")

                for monitor in monitors:
                    click.echo(f"ID: {monitor.id}")
                    click.echo(f"  {monitor.subject} {monitor.course_number} (Term: {monitor.term})")
                    if monitor.section_id:
                        click.echo(f"  Section: {monitor.section_id}")
                    click.echo(f"  Interval: {monitor.check_interval}s")
                    last_checked = monitor.last_checked.strftime("%Y-%m-%d %H:%M:%S") if monitor.last_checked else "Never"
                    click.echo(f"  Last checked: {last_checked}")
                    click.echo("")

            await checker.cleanup()

        except Exception as e:
            click.echo(f"Failed to list monitors: {e}", err=True)
            sys.exit(1)

    asyncio.run(run_list())


@cli.command()
@click.argument("monitor_id", type=int)
def remove(monitor_id: int):
    """Remove a course monitor"""
    async def run_remove():
        checker = CourseChecker()

        try:
            await checker.initialize()
            await checker.remove_course(monitor_id)

            click.echo(f"\n✓ Removed course monitor ID: {monitor_id}\n")

            await checker.cleanup()

        except Exception as e:
            click.echo(f"Failed to remove monitor: {e}", err=True)
            sys.exit(1)

    asyncio.run(run_remove())


@cli.command()
@click.option("-s", "--subject", required=True, help="Subject code")
@click.option("-n", "--number", required=True, help="Course number")
@click.option("-l", "--limit", type=int, default=20, help="Number of records to show")
def history(subject: str, number: str, limit: int):
    """View enrollment history for a course"""
    async def run_history():
        checker = CourseChecker()

        try:
            await checker.initialize()

            hist = checker.get_history(subject, number, limit)

            if not hist:
                click.echo("\nNo enrollment history found.\n")
            else:
                click.echo(f"\n📊 Enrollment History: {subject} {number}\n")

                for record in hist:
                    timestamp = record.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    click.echo(f"{timestamp} - Section {record.section_id}")
                    click.echo(f"  Status: {record.status}")
                    click.echo(f"  Seats: {record.open_seats}/{record.total_seats}")
                    click.echo(f"  Waitlist: {record.waitlist_open}/{record.waitlist_total}")
                    click.echo("")

            await checker.cleanup()

        except Exception as e:
            click.echo(f"Failed to get history: {e}", err=True)
            sys.exit(1)

    asyncio.run(run_history())


@cli.command()
def test_notify():
    """Test notification system"""
    async def run_test():
        checker = CourseChecker()

        try:
            await checker.initialize()

            click.echo("\nSending test notification...\n")

            await checker.notification_service.test_notifications()

            click.echo("✓ Test notification sent! Check your email/SMS.\n")

            await checker.cleanup()

        except Exception as e:
            click.echo(f"Failed to send test notification: {e}", err=True)
            sys.exit(1)

    asyncio.run(run_test())


if __name__ == "__main__":
    cli()
