# UW Madison Course Enrollment Checker

A real-time course availability monitoring tool that integrates with the UW Courses API to notify users when seats become available in desired courses.

## Project Structure

```
claude-hackathon/
├── frontend/              # React + TypeScript frontend (✅ Complete)
│   ├── src/              # Source code
│   ├── public/           # Static assets
│   ├── README.md         # Frontend documentation
│   ├── FRONTEND.md       # Detailed frontend guide
│   ├── INTEGRATION_GUIDE.md  # Backend integration guide
│   └── ARCHITECTURE.md   # Architecture documentation
│
├── backend/              # Python FastAPI backend (✅ Complete)
│   ├── src/             # Source code
│   ├── main.py          # Entry point
│   ├── test_api.py      # API tests
│   ├── README.md        # Backend documentation
│   └── requirements.txt # Python dependencies
│
├── README.md            # This file
├── QUICK_START.md       # Quick reference
└── .gitignore          # Git ignore rules
```

## Quick Start

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

### Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

The backend API will run on [http://localhost:8000](http://localhost:8000)

## Features

### Frontend (✅ Complete)
- 📊 Dashboard for monitoring multiple courses
- ➕ Add/remove courses with custom check intervals
- ⏸️ Pause/resume monitoring
- 🔔 Configure email, SMS, webhook notifications
- 📱 Responsive design (mobile + desktop)
- 🌙 Modern dark theme
- 🔧 Mock API for development (or connect to real backend)

### Backend (✅ Complete)
- 🚀 FastAPI-based REST API
- 📡 Real-time UW Courses API integration
- 💾 SQLite database for data persistence
- ⏰ Course monitoring service
- 🔔 Multi-channel notifications (email, SMS, webhook)
- 🎯 Flexible course search and filtering
- 📊 Enrollment history tracking

## System Components

```
┌─────────────────────────────────────────────────────────┐
│                     User Interface                      │
│            (React Web Dashboard - Frontend)             │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                  Backend API (FastAPI)                  │
│              REST endpoints for CRUD ops                │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                  Scheduler Service                      │
│         (Manages polling intervals & job queue)         │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                 API Integration Layer                   │
│              (UW Courses API Integration)               │
│  • Caching (60s TTL)    • Request throttling            │
│  • Error handling       • Response parsing              │
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
│                  Data Storage (SQLite)                  │
│  • Course configurations                                │
│  • Enrollment history                                   │
│  • User preferences                                     │
└─────────────────────────────────────────────────────────┘
```

## API Integration

### UW Courses API

- **Endpoint**: UW Courses API
- **Base URL**: `https://static.uwcourses.com`
- **Key Endpoint**: `/update.json` - Get real-time course enrollment data
- **Features**:
  - Automatic caching (60s TTL) to reduce API load
  - Rate limiting protection
  - Flexible data parsing for various response formats
  - No authentication required

### Rate Limiting

- Recommended: Maximum 60 requests per minute
- Implement exponential backoff on 429 errors
- Cache responses for 60 seconds to reduce load

## Technology Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for build tooling
- **axios** for HTTP requests
- **react-hot-toast** for notifications
- **lucide-react** for icons

### Backend
- **Python 3.9+**
- **FastAPI** - Modern web framework
- **SQLAlchemy** - Database ORM
- **httpx** - Async HTTP client
- **APScheduler** - Task scheduling
- **SQLite** - Database

## Documentation

### Root Level
- **[README.md](README.md)** - This file (project overview)
- **[QUICK_START.md](QUICK_START.md)** - Quick reference guide

### Frontend
- **[frontend/README.md](frontend/README.md)** - Quick start
- **[frontend/GETTING_STARTED.md](frontend/GETTING_STARTED.md)** - Step-by-step guide
- **[frontend/FRONTEND.md](frontend/FRONTEND.md)** - Complete documentation
- **[frontend/INTEGRATION_GUIDE.md](frontend/INTEGRATION_GUIDE.md)** - Backend integration
- **[frontend/ARCHITECTURE.md](frontend/ARCHITECTURE.md)** - Architecture details

### Backend
- **[backend/README.md](backend/README.md)** - Backend documentation
- **[backend/.env.example](backend/.env.example)** - Environment variables template

## Connecting Frontend to Backend

The frontend is designed to easily connect to the backend:

1. **In the frontend**, edit `src/services/api/index.ts`:
   ```typescript
   const USE_MOCK_API = false; // Switch to real API
   ```

2. **Create** `frontend/.env`:
   ```bash
   VITE_API_BASE_URL=http://localhost:8000/api
   ```

3. **Customize endpoints** (if needed) in `frontend/src/services/api/realAdapter.ts`

4. **Restart** the frontend dev server

See [frontend/INTEGRATION_GUIDE.md](frontend/INTEGRATION_GUIDE.md) for detailed integration instructions.

## Data Models

### Course Monitor Entry
```typescript
{
  id: string,
  term: string,
  subject: string,
  courseNumber: string,
  sections: string[],
  notifyOnOpen: boolean,
  notifyOnWaitlist: boolean,
  checkInterval: number,
  active: boolean,
  lastChecked?: Date,
  createdAt: Date
}
```

### Enrollment Snapshot
```typescript
{
  id: string,
  courseMonitorId: string,
  totalSeats: number,
  openSeats: number,
  enrolledSeats: number,
  waitlistTotal?: number,
  waitlistOpen?: number,
  status: 'OPEN' | 'CLOSED' | 'WAITLIST' | 'CANCELLED',
  timestamp: Date
}
```

See [frontend/src/services/api/types.ts](frontend/src/services/api/types.ts) for complete type definitions.

## Development Workflow

### Running Both Frontend and Backend

**Terminal 1 - Backend:**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Then configure the frontend to use the real API (see "Connecting Frontend to Backend" above).

### Development vs Production

**Development:**
- Frontend: Mock API enabled by default
- Backend: SQLite database
- No external services required

**Production:**
- Frontend: Connected to backend API
- Backend: Production database (PostgreSQL recommended)
- Email/SMS services configured
- Proper environment variables set

## Configuration

### Backend Environment Variables

See [backend/.env.example](backend/.env.example) for a complete list. Key variables:

```bash
# API Configuration
API_BASE_URL=https://static.uwcourses.com
API_UPDATE_ENDPOINT=/update.json
REQUEST_TIMEOUT=10

# Notification Settings
EMAIL_ENABLED=true
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_FROM=noreply@example.com
EMAIL_TO=student@wisc.edu

# Monitoring Settings
CHECK_INTERVAL=300  # 5 minutes in seconds
```

### Frontend Environment Variables

See [frontend/.env.example](frontend/.env.example):

```bash
# Backend API URL
VITE_API_BASE_URL=http://localhost:8000/api
```

## Testing

### Frontend
```bash
cd frontend
npm run build  # Test production build
```

### Backend
```bash
cd backend
python test_api.py  # Test UW Courses API integration
```

## Deployment

### Frontend
```bash
cd frontend
npm run build
# Deploy the dist/ directory to your static hosting service
```

### Backend
The backend can be deployed to:
- Heroku
- AWS Lambda
- Google Cloud Run
- DigitalOcean App Platform
- Any Python-compatible hosting service

See [backend/README.md](backend/README.md) for deployment instructions.

## Future Enhancements

- [ ] User authentication and multi-user support
- [ ] Mobile app for iOS and Android
- [ ] Machine learning for predicting seat openings
- [ ] Support for multiple universities
- [ ] Browser extension for inline availability checking
- [ ] Automatic enrollment when seats open (with user authentication)
- [ ] Advanced analytics dashboard

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see `LICENSE` file for details

## Disclaimer

This tool is for educational purposes and personal use. Always comply with UW Madison's terms of service and acceptable use policies. Do not abuse the API or create excessive load on university systems. Be respectful of rate limits and use reasonable check intervals.

## Support

For questions or issues:
- Open an issue on GitHub
- Check the documentation in `frontend/` and `backend/` directories

## Acknowledgments

- UW Madison for providing public course enrollment data
- UW Courses API for the real-time data endpoint
- Contributors and testers
- Open source libraries used in this project
