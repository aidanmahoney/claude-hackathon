# UW Madison Course Checker - Python Backend

Complete Python backend for monitoring UW Madison course enrollment using the **uwcourses.com API**.

## 🎯 Features

- ✅ Real-time monitoring using `https://static.uwcourses.com/update.json`
- ✅ Smart caching (60s TTL) to reduce API load
- ✅ Multi-channel notifications (Email, SMS, Webhooks)
- ✅ SQLAlchemy database with enrollment history
- ✅ APScheduler for automated checking
- ✅ Click CLI with 7 commands
- ✅ Flexible data parsing for various API formats

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your settings

# 3. Test API connection
python test_api.py

# 4. Add a course
python main.py add --term 1252 --subject "COMP SCI" --number 400

# 5. Start monitoring
python main.py monitor
```

## 📋 CLI Commands

### Monitor Courses
```bash
python main.py monitor
```
Starts continuous monitoring of all active courses.

### Check Once
```bash
python main.py check --term 1252 --subject "COMP SCI" --number 400
```
One-time check without adding to monitors.

### Add Course
```bash
python main.py add \
  --term 1252 \
  --subject "COMP SCI" \
  --number 400 \
  --section 001 \
  --interval 300 \
  --notify-open
```

### List Active Monitors
```bash
python main.py list
```

### Remove Monitor
```bash
python main.py remove <monitor_id>
```

### View History
```bash
python main.py history --subject "COMP SCI" --number 400
```

### Test Notifications
```bash
python main.py test-notify
```

## ⚙️ Configuration

Edit `.env` file:

```env
# API - Uses uwcourses.com
API_BASE_URL=https://static.uwcourses.com
API_UPDATE_ENDPOINT=/update.json

# Email Notifications
EMAIL_ENABLED=true
EMAIL_SMTP_USER=your_email@gmail.com
EMAIL_SMTP_PASS=your_app_password
EMAIL_TO=student@wisc.edu

# SMS (Optional)
SMS_ENABLED=false
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token

# Monitoring
CHECK_INTERVAL=300  # seconds
DATABASE_URL=sqlite:///./data/courses.db
```

## 🏗️ Architecture

```
backend/
├── src/
│   ├── api/
│   │   └── uw_madison_api.py    # API client with caching
│   ├── database/
│   │   ├── models.py             # SQLAlchemy models
│   │   └── database.py           # Database operations
│   ├── services/
│   │   ├── course_checker.py     # Monitoring service
│   │   └── notification_service.py # Notifications
│   ├── utils/
│   │   └── logger.py             # Logging
│   ├── config.py                 # Settings
│   └── cli.py                    # CLI commands
├── main.py                       # Entry point
├── test_api.py                   # API test script
└── requirements.txt              # Dependencies
```

## 🔌 API Integration

This backend uses `https://static.uwcourses.com/update.json`:
- **No authentication required**
- **Public access** for educational use
- **Real-time data** on course enrollment
- **Automatic caching** to minimize requests

### Testing the API
```bash
python test_api.py
```

This will:
1. Fetch data from the API
2. Show available data structure
3. Let you test specific course lookups

## 📊 Database Schema

### `course_monitors`
- Course monitoring configuration
- Check intervals and notification preferences
- Active/inactive status

### `enrollment_snapshots`
- Historical enrollment data
- Seat counts and waitlist info
- Timestamps for trend analysis

### `notifications`
- Notification history
- Success/failure tracking
- Message details

## 📧 Email Setup (Gmail)

1. Enable 2FA on your Google account
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use in `.env`:
```env
EMAIL_SMTP_USER=your_email@gmail.com
EMAIL_SMTP_PASS=your_16_char_app_password
```

## 🔧 Technology Stack

- **Python 3.9+**: Core language
- **httpx**: Async HTTP client
- **SQLAlchemy 2.0**: Database ORM
- **APScheduler**: Task scheduling
- **Click**: CLI framework
- **Pydantic**: Settings validation
- **Twilio**: SMS (optional)

## 📝 Example Usage

### Monitor Multiple Sections
```bash
python main.py add --term 1252 --subject "COMP SCI" --number 400 --section 001
python main.py add --term 1252 --subject "COMP SCI" --number 400 --section 002
```

### Fast Checking for Popular Courses
```bash
python main.py add \
  --term 1252 \
  --subject "COMP SCI" \
  --number 400 \
  --interval 120  # Check every 2 minutes
```

### Waitlist Only
```bash
python main.py add \
  --term 1252 \
  --subject "COMP SCI" \
  --number 400 \
  --no-notify-open \
  --notify-waitlist
```

## 🐛 Troubleshooting

### Import Errors
Make sure you're in the backend directory and have installed dependencies:
```bash
cd backend
pip install -r requirements.txt
```

### Email Not Sending
- Check `EMAIL_ENABLED=true` in `.env`
- Verify Gmail app password
- Test with: `python main.py test-notify`

### Course Not Found
- Verify term code (e.g., "1252" for Spring 2025)
- Check exact subject spelling (e.g., "COMP SCI" not "CS")
- Run `python test_api.py` to see available data

### API Errors
- Check internet connection
- Verify API is accessible: `curl https://static.uwcourses.com/update.json`
- Check logs in `logs/error.log`

## 📄 License

MIT License - Free for educational use

## ⚠️ Disclaimer

- Educational and personal use only
- Respect API rate limits (max 60 req/min)
- Use reasonable check intervals
- Comply with UW Madison's terms of service
- No excessive server load

## 🤝 Contributing

The codebase is modular and easy to extend:
- Add notification channels in `notification_service.py`
- Extend database schema in `models.py`
- Add CLI commands in `cli.py`

---

**Built for UW Madison students** 🎓
