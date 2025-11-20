# UW Madison Course Enrollment Checker

A real-time course availability monitoring tool that integrates with the UW Madison Course Search and Enroll API to notify users when seats become available in desired courses.

## Overview

This tool continuously monitors UW Madison course enrollment status and provides automated notifications when a course opens up for enrollment. Built for students who need to get into full courses, this system checks availability at configurable intervals and alerts users through multiple notification channels.

## Features

- **Real-time Monitoring**: Automatically checks course availability at specified intervals
- **Multi-course Tracking**: Monitor multiple courses and sections simultaneously
- **Smart Notifications**: Receive alerts via email, SMS, or webhook when seats open up
- **Historical Data**: Track enrollment patterns and availability trends
- **Seat Count Tracking**: Monitor total seats, open seats, and waitlist status
- **Term Management**: Support for multiple academic terms
- **Rate Limiting**: Respects API rate limits to ensure reliable operation

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                     User Interface                      │
│            (CLI / Web Dashboard / Config File)          │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                  Scheduler Service                      │
│         (Manages polling intervals & job queue)         │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                 API Integration Layer                   │
│        (UW Madison Course Search & Enroll API)          │
│  • Authentication    • Request throttling               │
│  • Error handling    • Response parsing                 │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│              Availability Detector                      │
│  • Compare current vs. previous state                   │
│  • Detect seat openings                                 │
│  • Filter notification criteria                         │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│              Notification Service                       │
│  • Email (SMTP)     • SMS (Twilio)                      │
│  • Webhooks         • Push notifications                │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                  Data Storage                           │
│  • Course configurations                                │
│  • Enrollment history                                   │
│  • User preferences                                     │
└─────────────────────────────────────────────────────────┘
```

### Component Details

#### 1. API Integration Layer
- **Endpoint**: UW Courses API
- **Base URL**: `https://static.uwcourses.com`
- **Key Endpoints**:
  - `/update.json` - Get real-time course enrollment data
- **Features**:
  - Automatic caching (60s TTL) to reduce API load
  - Rate limiting protection
  - Flexible data parsing for various response formats

#### 2. Scheduler Service
- Manages polling intervals (default: 2-5 minutes)
- Implements exponential backoff on errors
- Distributes API calls to avoid rate limiting
- Supports configurable check frequencies per course

#### 3. Availability Detector
- Compares current enrollment data with previous state
- Triggers notifications on state changes:
  - Closed → Open
  - Waitlist available
  - Seat count increase
- Implements debouncing to prevent duplicate notifications

#### 4. Notification Service
- Multi-channel notification support
- Configurable notification templates
- Delivery confirmation and retry logic
- Priority-based notification queuing

## Installation

### Prerequisites
- Node.js 18+ or Python 3.9+
- Database (SQLite, PostgreSQL, or MongoDB)
- API credentials (if required by UW Madison)

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd uw-course-checker

# Install dependencies
npm install
# or
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your settings

# Initialize database
npm run db:init
# or
python manage.py init

# Start the service
npm start
# or
python main.py
```

## Configuration

### Environment Variables

```bash
# API Configuration
API_BASE_URL=https://static.uwcourses.com
API_UPDATE_ENDPOINT=/update.json
REQUEST_TIMEOUT=10
RATE_LIMIT_REQUESTS=60
RATE_LIMIT_WINDOW=60

# Notification Settings
EMAIL_ENABLED=true
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_FROM=noreply@example.com
EMAIL_TO=student@wisc.edu

SMS_ENABLED=true
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_FROM=+1234567890
TWILIO_PHONE_TO=+1234567890

# Monitoring Settings
CHECK_INTERVAL=300000  # 5 minutes in milliseconds
MAX_RETRIES=3
RETRY_BACKOFF=2

# Database
DB_TYPE=sqlite
DB_PATH=./data/courses.db
```

### Course Configuration

Create a `courses.json` file to specify which courses to monitor:

```json
{
  "courses": [
    {
      "term": "1252",
      "subject": "COMP SCI",
      "courseNumber": "400",
      "sections": ["001", "002"],
      "notifyOnOpen": true,
      "notifyOnWaitlist": false,
      "checkInterval": 300000
    },
    {
      "term": "1252",
      "subject": "MATH",
      "courseNumber": "340",
      "sections": ["all"],
      "notifyOnOpen": true,
      "notifyOnWaitlist": true,
      "checkInterval": 180000
    }
  ]
}
```

## Usage

### Command Line Interface

```bash
# Start monitoring all configured courses
npm run monitor

# Check a specific course once
npm run check -- --term 1252 --subject "COMP SCI" --number 400

# Add a course to monitoring list
npm run add-course -- --term 1252 --subject "COMP SCI" --number 400 --section 001

# View enrollment history
npm run history -- --subject "COMP SCI" --number 400

# Test notifications
npm run test-notify
```

### Programmatic Usage

```javascript
const CourseChecker = require('./src/CourseChecker');

const checker = new CourseChecker({
  term: '1252',
  subject: 'COMP SCI',
  courseNumber: '400',
  sections: ['001']
});

// Start monitoring
await checker.start();

// Listen for availability changes
checker.on('available', (courseData) => {
  console.log('Course now available!', courseData);
});

// Stop monitoring
await checker.stop();
```

## UW Courses API Integration

### Authentication
The UW Courses API (`https://static.uwcourses.com`) is publicly accessible for read-only course information. No authentication is required.

### API Request Example

```python
import httpx

async def get_course_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://static.uwcourses.com/update.json")
        return response.json()

# The API returns real-time enrollment data for all courses
data = await get_course_data()
```

### Features
- **Real-time Data**: Updated enrollment information
- **No Authentication**: Public API, no keys required
- **Caching**: Built-in 60-second cache to reduce API load
- **Flexible Parsing**: Supports various response formats

### Rate Limiting
- Recommended: Maximum 60 requests per minute
- Implement exponential backoff on 429 errors
- Cache responses for 1-2 minutes to reduce load

## Technology Stack

### Backend Options

**Node.js Stack:**
- Runtime: Node.js 18+
- Framework: Express.js
- Scheduler: node-cron
- HTTP Client: axios
- Database: Sequelize (SQLite/PostgreSQL)

**Python Stack:**
- Runtime: Python 3.9+
- Framework: FastAPI
- Scheduler: APScheduler
- HTTP Client: httpx
- Database: SQLAlchemy (SQLite/PostgreSQL)

### Frontend (Optional Dashboard)
- React.js with TypeScript
- Chart.js for enrollment trends
- WebSocket for real-time updates

### Infrastructure
- Docker & Docker Compose for deployment
- GitHub Actions for CI/CD
- Monitoring: Prometheus & Grafana

## Data Models

### Course Monitor Entry
```javascript
{
  id: string,
  term: string,
  subject: string,
  courseNumber: string,
  sectionId: string,
  userId: string,
  active: boolean,
  checkInterval: number,
  lastChecked: timestamp,
  createdAt: timestamp
}
```

### Enrollment Snapshot
```javascript
{
  id: string,
  courseMonitorId: string,
  totalSeats: number,
  openSeats: number,
  enrolledSeats: number,
  waitlistTotal: number,
  waitlistOpen: number,
  status: string,
  timestamp: timestamp
}
```

## Error Handling

- **Network Errors**: Automatic retry with exponential backoff
- **API Rate Limits**: Queue requests and respect retry-after headers
- **Invalid Course Data**: Log errors and notify administrator
- **Notification Failures**: Retry notifications up to 3 times
- **Database Errors**: Graceful degradation with in-memory fallback

## Future Enhancements

- [ ] Mobile app for iOS and Android
- [ ] Machine learning for predicting seat openings
- [ ] Support for multiple universities
- [ ] Browser extension for inline availability checking
- [ ] Automatic enrollment when seats open (with user authentication)
- [ ] Group notification for study groups
- [ ] Integration with calendar apps
- [ ] Advanced filtering (instructor, time, location)

## Contributing

Contributions are welcome! Please read `CONTRIBUTING.md` for details on our code of conduct and the process for submitting pull requests.

## License

MIT License - see `LICENSE` file for details

## Disclaimer

This tool is for educational purposes and personal use. Always comply with UW Madison's terms of service and acceptable use policies. Do not abuse the API or create excessive load on university systems. Be respectful of rate limits and use reasonable check intervals.

## Support

For questions or issues:
- Open an issue on GitHub
- Email: support@example.com
- Documentation: [Wiki](wiki-link)

## Acknowledgments

- UW Madison for providing public course enrollment data
- Contributors and testers
- Open source libraries used in this project
