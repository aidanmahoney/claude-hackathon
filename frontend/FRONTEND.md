# Frontend Documentation

## Quick Start

```bash
npm install
npm run dev
```

The app will run at `http://localhost:5173`

## Switching Between Mock and Real API

The frontend is designed with a flexible API adapter pattern that makes it easy to switch between mock data (for development) and your real backend API.

### Using Mock API (Default)

By default, the app uses mock data. This is perfect for development and testing the UI without needing a backend.

**File:** [src/services/api/index.ts](src/services/api/index.ts#L12)

```typescript
const USE_MOCK_API = true; // Currently using mock data
```

### Switching to Real API

When your backend engineer has the API ready:

1. **Update the configuration in [src/services/api/index.ts](src/services/api/index.ts#L12)**:
   ```typescript
   const USE_MOCK_API = false; // Switch to real API
   ```

2. **Create a `.env` file** (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```

3. **Update the API base URL** in `.env`:
   ```
   VITE_API_BASE_URL=http://your-backend-url.com/api
   ```

4. **Adjust API endpoints** in [src/services/api/realAdapter.ts](src/services/api/realAdapter.ts) to match your backend's actual endpoints:
   ```typescript
   // Example: Change this
   async getMonitoredCourses(): Promise<MonitoredCourse[]> {
     const response = await this.client.get('/monitors'); // ← Adjust this endpoint
     return this.transformMonitoredCoursesResponse(response.data);
   }
   ```

5. **Update data transformations** if your backend returns data in a different format:
   ```typescript
   private transformMonitoredCourseResponse(data: any): MonitoredCourse {
     return {
       id: data.id,  // ← Adjust field names to match your backend
       term: data.term,
       subject: data.subject,
       // ... etc
     };
   }
   ```

## API Adapter Architecture

The frontend uses an **Adapter Pattern** to abstract away the API implementation:

```
src/services/api/
├── types.ts           # TypeScript types/interfaces
├── apiAdapter.ts      # Interface definition (contract)
├── mockAdapter.ts     # Mock implementation for development
├── realAdapter.ts     # Real API implementation (to be customized)
└── index.ts           # Main export and configuration
```

### How It Works

1. **Interface Definition** ([apiAdapter.ts](src/services/api/apiAdapter.ts)): Defines the contract that any API implementation must follow
2. **Mock Implementation** ([mockAdapter.ts](src/services/api/mockAdapter.ts)): Provides fake data for development
3. **Real Implementation** ([realAdapter.ts](src/services/api/realAdapter.ts)): Connects to your actual backend (needs customization)
4. **Configuration** ([index.ts](src/services/api/index.ts)): Switches between mock and real implementations

## Backend API Endpoints Expected

The frontend expects the following endpoints (these can be customized in [realAdapter.ts](src/services/api/realAdapter.ts)):

### Courses
- `GET /courses/search?term=1252&subject=COMP%20SCI&courseNumber=400` - Search courses
- `GET /courses/:term/:subject/:courseNumber` - Get course details

### Monitored Courses
- `GET /monitors` - Get all monitored courses
- `POST /monitors` - Add a course to monitoring
- `PATCH /monitors/:id` - Update a monitored course
- `DELETE /monitors/:id` - Remove a monitored course
- `GET /monitors/:id/history` - Get enrollment history

### Notification Preferences
- `GET /preferences/notifications` - Get notification preferences
- `PUT /preferences/notifications` - Update notification preferences
- `POST /notifications/test` - Test a notification

## Data Types

All TypeScript types are defined in [src/services/api/types.ts](src/services/api/types.ts):

```typescript
interface MonitoredCourse {
  id: string;
  term: string;
  subject: string;
  courseNumber: string;
  sections: string[];
  notifyOnOpen: boolean;
  notifyOnWaitlist: boolean;
  checkInterval: number;
  active: boolean;
  lastChecked?: Date;
  createdAt: Date;
}
```

## Customizing for Your Backend

### Step 1: Update Endpoint URLs

In [src/services/api/realAdapter.ts](src/services/api/realAdapter.ts), update the endpoint paths:

```typescript
async getMonitoredCourses(): Promise<MonitoredCourse[]> {
  // Change '/monitors' to match your backend endpoint
  const response = await this.client.get('/your-endpoint-path');
  return this.transformMonitoredCoursesResponse(response.data);
}
```

### Step 2: Update Data Transformations

If your backend returns data in a different format, update the transformation methods:

```typescript
private transformMonitoredCourseResponse(data: any): MonitoredCourse {
  return {
    // Map your backend fields to frontend fields
    id: data._id,  // e.g., if your backend uses _id instead of id
    term: data.semester,  // e.g., if your backend calls it 'semester'
    // ... etc
  };
}
```

### Step 3: Handle Authentication

If your backend requires authentication, update the request interceptor in [realAdapter.ts](src/services/api/realAdapter.ts):

```typescript
this.client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  }
);
```

## Building for Production

```bash
npm run build
```

This creates optimized production files in the `dist/` directory.

## Project Structure

```
src/
├── components/           # React components
│   ├── CourseCard.tsx   # Course monitoring card
│   ├── AddCourseModal.tsx  # Add course modal
│   └── NotificationSettings.tsx  # Notification preferences
├── services/
│   └── api/             # API service layer
│       ├── types.ts
│       ├── apiAdapter.ts
│       ├── mockAdapter.ts
│       ├── realAdapter.ts
│       └── index.ts
├── App.tsx              # Main application component
├── index.css            # Global styles
└── main.tsx             # Application entry point
```

## Features Implemented

- **Course Monitoring Dashboard**: View all monitored courses
- **Add/Remove Courses**: Modal to add courses with configuration
- **Pause/Resume Monitoring**: Toggle monitoring for individual courses
- **Notification Settings**: Configure email, SMS, and webhook notifications
- **Toast Notifications**: User feedback for all actions
- **Responsive Design**: Works on desktop and mobile
- **Dark Theme**: Modern dark UI with good contrast

## Dependencies

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **axios** - HTTP client
- **react-hot-toast** - Toast notifications
- **lucide-react** - Icons

## Notes for Backend Engineer

The frontend is ready to integrate with your API. Here's what you need to know:

1. **All API endpoints** are defined in [src/services/api/realAdapter.ts](src/services/api/realAdapter.ts)
2. **Expected data formats** are in [src/services/api/types.ts](src/services/api/types.ts)
3. **Transformation functions** handle any differences between your API format and the frontend's expected format
4. The frontend currently uses **mock data**, so you can see the UI in action before the backend is ready
5. Switching to your API is as simple as setting `USE_MOCK_API = false` in [src/services/api/index.ts](src/services/api/index.ts)

Feel free to adjust any endpoints or data structures in `realAdapter.ts` to match your backend implementation!
