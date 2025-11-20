# UW Madison Course Enrollment Checker - Frontend

A modern, responsive React application for monitoring UW Madison course enrollment status with real-time notifications.

## Quick Start

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

## Documentation

📖 **[Frontend Documentation](FRONTEND.md)** - Complete guide for frontend development
🔌 **[Integration Guide](INTEGRATION_GUIDE.md)** - Guide for backend engineers
🏗️ **[Architecture](ARCHITECTURE.md)** - Detailed architecture explanation

## Features

- **Course Monitoring Dashboard**: View and manage all monitored courses
- **Add/Remove Courses**: Easy modal interface for course configuration
- **Pause/Resume**: Toggle monitoring for individual courses
- **Notification Settings**: Configure email, SMS, and webhook notifications
- **Responsive Design**: Works on desktop and mobile
- **Dark Theme**: Modern UI with excellent contrast
- **Mock API**: Test the UI without a backend

## Architecture Highlights

### Flexible API Layer

The frontend uses an **adapter pattern** that makes it incredibly easy to switch between mock data and your real backend:

```typescript
// Switch between mock and real API
const USE_MOCK_API = true; // Just flip this to false
```

### Easy Backend Integration

When your backend is ready:

1. Set `USE_MOCK_API = false` in `src/services/api/index.ts`
2. Update `.env` with your API URL
3. Optionally adjust endpoints/transformations in `realAdapter.ts`

That's it! The frontend handles everything else.

## Project Structure

```
frontend/
├── src/
│   ├── components/           # React components
│   │   ├── CourseCard.tsx
│   │   ├── AddCourseModal.tsx
│   │   └── NotificationSettings.tsx
│   ├── services/api/         # API service layer (adapter pattern)
│   │   ├── types.ts         # TypeScript interfaces
│   │   ├── apiAdapter.ts    # API contract
│   │   ├── mockAdapter.ts   # Mock implementation
│   │   ├── realAdapter.ts   # Real API implementation
│   │   └── index.ts         # Configuration
│   ├── App.tsx              # Main app component
│   └── index.css            # Global styles
├── public/                   # Static assets
├── dist/                     # Build output
├── package.json
├── vite.config.ts
└── tsconfig.json
```

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **axios** - HTTP client
- **react-hot-toast** - Toast notifications
- **lucide-react** - Icons

## Build

```bash
npm run build
```

Production files are output to `dist/`

## Why This Architecture?

The adapter pattern provides:

✅ **Zero coupling** - Frontend and backend are completely independent
✅ **Easy testing** - Use mock data while backend is in development
✅ **Flexible integration** - Adjust endpoints and data formats easily
✅ **Type safety** - Full TypeScript support
✅ **Clear contract** - Well-defined API interface

## For Backend Engineers

See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) for:
- Expected API endpoints
- Data models and types
- How to customize the adapter
- CORS configuration
- Authentication setup

The frontend is designed to be **moldable** - you can easily adjust it to fit whatever API structure you design!
