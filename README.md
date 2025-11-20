# UW Madison Course Enrollment Checker

A real-time course availability monitoring tool that integrates with the UW Madison Course Search and Enroll API to notify users when seats become available in desired courses.

## Project Structure

```
claude-hackathon/
├── frontend/              # React + TypeScript frontend
│   ├── src/              # Source code
│   ├── public/           # Static assets
│   ├── README.md         # Frontend documentation
│   ├── FRONTEND.md       # Detailed frontend guide
│   ├── INTEGRATION_GUIDE.md  # Backend integration guide
│   └── ARCHITECTURE.md   # Architecture documentation
├── backend/              # (To be implemented)
└── README.md            # This file
```

## Frontend

The frontend is **fully functional** and ready to use with mock data!

### Quick Start

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) to see the application.

### Features

- ✅ Course monitoring dashboard
- ✅ Add/remove courses to monitor
- ✅ Pause/resume monitoring
- ✅ Notification settings (email, SMS, webhook)
- ✅ Responsive design
- ✅ Mock API for development
- ✅ Easy backend integration

### Documentation

- **[frontend/README.md](frontend/README.md)** - Quick start and overview
- **[frontend/FRONTEND.md](frontend/FRONTEND.md)** - Complete frontend guide
- **[frontend/INTEGRATION_GUIDE.md](frontend/INTEGRATION_GUIDE.md)** - How to integrate with backend
- **[frontend/ARCHITECTURE.md](frontend/ARCHITECTURE.md)** - Architecture details

## Backend

The backend is not yet implemented. When you create it, place it in a `backend/` directory.

### API Integration

The frontend uses an **adapter pattern** that makes integration simple:

1. The frontend currently uses mock data
2. When your backend is ready, just change one line: `USE_MOCK_API = false`
3. The frontend will automatically connect to your API
4. You can customize endpoints and data transformations as needed

See [frontend/INTEGRATION_GUIDE.md](frontend/INTEGRATION_GUIDE.md) for complete integration instructions.

## Overview

This tool continuously monitors UW Madison course enrollment status and provides automated notifications when a course opens up for enrollment.

### Key Features

- **Real-time Monitoring**: Automatically checks course availability at specified intervals
- **Multi-course Tracking**: Monitor multiple courses and sections simultaneously
- **Smart Notifications**: Receive alerts via email, SMS, or webhook when seats open up
- **Historical Data**: Track enrollment patterns and availability trends
- **Seat Count Tracking**: Monitor total seats, open seats, and waitlist status
- **Term Management**: Support for multiple academic terms
- **Rate Limiting**: Respects API rate limits to ensure reliable operation

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                     User Interface                      │
│                 (React Web Dashboard)                   │
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

## UW Madison API Integration

### API Information

- **Base URL**: `https://public.enroll.wisc.edu/api`
- **Key Endpoints**:
  - `/search/v1/enrollmentStatus/{term}/{courseId}` - Get enrollment status
  - `/search/v1/courses` - Search courses
  - `/search/v1/sections/{sectionId}` - Get section details

### Rate Limiting

- Recommended: Maximum 60 requests per minute
- Implement exponential backoff on 429 errors
- Cache responses for 1-2 minutes to reduce load

## Technology Stack

### Frontend (✅ Implemented)
- **React 18** with TypeScript
- **Vite** for build tooling
- **axios** for HTTP requests
- **react-hot-toast** for notifications
- **lucide-react** for icons

### Backend (To be implemented)

**Node.js Stack Option:**
- Runtime: Node.js 18+
- Framework: Express.js
- Scheduler: node-cron
- HTTP Client: axios
- Database: Sequelize (SQLite/PostgreSQL)

**Python Stack Option:**
- Runtime: Python 3.9+
- Framework: FastAPI
- Scheduler: APScheduler
- HTTP Client: httpx
- Database: SQLAlchemy (SQLite/PostgreSQL)

## Development Workflow

### Current Status

✅ Frontend complete and fully functional
⏳ Backend to be implemented
⏳ Database schema to be designed
⏳ API endpoints to be created
⏳ Notification system to be implemented

### Getting Started

1. **Run the frontend** to see the UI and understand the requirements:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

2. **Review the integration guide** to understand what the backend needs to provide:
   - See [frontend/INTEGRATION_GUIDE.md](frontend/INTEGRATION_GUIDE.md)
   - Check expected API endpoints
   - Review data models in [frontend/src/services/api/types.ts](frontend/src/services/api/types.ts)

3. **Implement the backend** in a `backend/` directory:
   - Create API endpoints that match the interface
   - Or customize the frontend adapter to match your API
   - The adapter pattern makes integration flexible!

4. **Connect frontend to backend**:
   - Change `USE_MOCK_API = false` in frontend
   - Set backend URL in `.env`
   - Test integration

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

## Future Enhancements

- [ ] Backend API implementation
- [ ] Database setup and migrations
- [ ] Actual course monitoring service
- [ ] Email/SMS notification integration
- [ ] Mobile app for iOS and Android
- [ ] Machine learning for predicting seat openings
- [ ] Support for multiple universities
- [ ] Browser extension for inline availability checking
- [ ] Automatic enrollment when seats open (with user authentication)

## Contributing

Contributions are welcome! Please read `CONTRIBUTING.md` for details on our code of conduct and the process for submitting pull requests.

## License

MIT License - see `LICENSE` file for details

## Disclaimer

This tool is for educational purposes and personal use. Always comply with UW Madison's terms of service and acceptable use policies. Do not abuse the API or create excessive load on university systems. Be respectful of rate limits and use reasonable check intervals.

## Support

For questions or issues:
- Open an issue on GitHub
- Check the documentation in the `frontend/` directory

## Acknowledgments

- UW Madison for providing public course enrollment data
- Contributors and testers
- Open source libraries used in this project
