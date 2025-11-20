# UW Madison Course Checker - Python Backend

Python backend implementation for the UW Madison Course Enrollment Checker.

## Features

- 🔄 Real-time course availability monitoring
- 📧 Multi-channel notifications (Email, SMS, Webhooks)
- 📊 Historical enrollment tracking
- ⚡ Async API integration with rate limiting
- 🗄️ SQLAlchemy database with SQLite/PostgreSQL support
- 🖥️ CLI interface with Click

## Installation

### Prerequisites

- Python 3.9 or higher
- pip

### Setup

1. **Clone and navigate to backend:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Initialize database:**
```bash
python -c "from src.database.database import Database; Database().initialize()"
```

## Usage

### Command Line Interface

The tool provides several commands for managing course monitoring:

#### Start Monitoring
Monitor all configured courses continuously:
```bash
python main.py monitor
```

#### Check a Course Once
Check a specific course without adding to monitors:
```bash
python main.py check --term 1252 --subject "COMP SCI" --number 400
```

#### Add Course to Monitor
Add a course to the monitoring list:
```bash
python main.py add \
  --term 1252 \
  --subject "COMP SCI" \
  --number 400 \
  --section 001 \
  --interval 300 \
  --notify-open \
  --notify-waitlist
```

Parameters:
- `--term`: Term code (e.g., "1252" for Spring 2025)
- `--subject`: Subject code (e.g., "COMP SCI")
- `--number`: Course number (e.g., "400")
- `--section`: (Optional) Specific section to monitor
- `--interval`: Check interval in seconds (default: 300)
- `--notify-open`: Notify when seats become available
- `--notify-waitlist`: Notify when waitlist opens

#### List Active Monitors
View all courses being monitored:
```bash
python main.py list
```

#### Remove Monitor
Stop monitoring a course:
```bash
python main.py remove <monitor_id>
```

#### View History
See enrollment history for a course:
```bash
python main.py history --subject "COMP SCI" --number 400 --limit 50
```

#### Test Notifications
Verify notification system is working:
```bash
python main.py test-notify
```

### Programmatic Usage

You can also use the CourseChecker class programmatically:

```python
import asyncio
from src.services.course_checker import CourseChecker

async def main():
    checker = CourseChecker()
    await checker.initialize()

    # Add a course to monitor
    monitor_id = await checker.add_course(
        term="1252",
        subject="COMP SCI",
        course_number="400",
        notify_on_open=True,
        check_interval=300
    )

    # Start monitoring
    await checker.start()

    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await checker.cleanup()

asyncio.run(main())
```

## Configuration

### Environment Variables

Edit `.env` file with your configuration:

```env
# Email Notifications
EMAIL_ENABLED=true
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=your_email@gmail.com
EMAIL_SMTP_PASS=your_app_password
EMAIL_FROM=noreply@example.com
EMAIL_TO=student@wisc.edu

# SMS Notifications (Twilio)
SMS_ENABLED=false
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_FROM=+1234567890
TWILIO_PHONE_TO=+1234567890

# Webhook
WEBHOOK_ENABLED=false
WEBHOOK_URL=https://your-webhook-url.com/notify

# Monitoring
CHECK_INTERVAL=300  # seconds
LOG_LEVEL=INFO

# Database
DATABASE_URL=sqlite:///./data/courses.db
# Or for PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/courses
```

### Email Setup (Gmail Example)

1. Enable 2-factor authentication on your Google account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use the app password in `EMAIL_SMTP_PASS`

## Architecture

```
backend/
├── src/
│   ├── api/
│   │   └── uw_madison_api.py       # UW Madison API client
│   ├── database/
│   │   ├── models.py                # SQLAlchemy models
│   │   └── database.py              # Database operations
│   ├── services/
│   │   ├── course_checker.py        # Main monitoring service
│   │   └── notification_service.py  # Notification handler
│   ├── utils/
│   │   └── logger.py                # Logging configuration
│   ├── config.py                    # App configuration
│   └── cli.py                       # Command-line interface
├── data/                            # SQLite database (generated)
├── logs/                            # Log files (generated)
├── main.py                          # Entry point
├── requirements.txt                 # Python dependencies
└── setup.py                         # Package setup
```

## Technology Stack

- **Python 3.9+**: Core language
- **httpx**: Async HTTP client for API requests
- **SQLAlchemy 2.0**: Database ORM
- **APScheduler**: Task scheduling
- **Click**: CLI framework
- **Pydantic**: Settings and validation
- **Twilio**: SMS notifications
- **smtplib**: Email notifications

## Database Schema

### CourseMonitor
Stores course monitoring configurations:
- `id`, `term`, `subject`, `course_number`, `section_id`
- `notify_on_open`, `notify_on_waitlist`
- `check_interval`, `active`, `last_checked`

### EnrollmentSnapshot
Historical enrollment data:
- `monitor_id`, `section_id`, `class_number`
- `total_seats`, `enrolled_seats`, `open_seats`
- `waitlist_total`, `waitlist_enrolled`, `waitlist_open`
- `status`, `instructor`, `timestamp`

### Notification
Notification history:
- `monitor_id`, `section_id`, `notification_type`
- `message`, `sent_at`, `success`

## Error Handling

- **API Errors**: Automatic retry with exponential backoff
- **Rate Limiting**: Respects API rate limits, queues requests
- **Network Issues**: Graceful degradation, logged errors
- **Database Errors**: Transaction rollback, error logging

## Development

### Running Tests
```bash
# TODO: Add tests
pytest
```

### Code Style
```bash
# Format code
black src/
isort src/

# Lint code
flake8 src/
mypy src/
```

## Troubleshooting

### Email not sending
- Verify SMTP credentials
- Check firewall/antivirus settings
- Use app-specific password for Gmail

### Database locked errors
- Only one process should write to SQLite at a time
- Consider using PostgreSQL for concurrent access

### Import errors
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

## License

MIT License - see LICENSE file for details

## Disclaimer

This tool is for educational purposes and personal use. Always comply with UW Madison's terms of service and acceptable use policies. Use reasonable check intervals to avoid excessive API load.
