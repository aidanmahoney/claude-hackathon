# Backend Integration Guide

This guide is for the backend engineer to understand how to integrate with the frontend.

## Quick Overview

The frontend is **fully functional** and uses **mock data** by default. This means:
- You can run and test the UI immediately without any backend
- When your backend is ready, switching is just a configuration change
- The API layer is completely abstracted and moldable

## Current Status

✅ Frontend is complete and tested
✅ Build passes successfully
✅ Using mock API adapter for development
⏳ Ready to switch to real API when backend is ready

## How to Run the Frontend

```bash
npm install
npm run dev
```

Open `http://localhost:5173` to see the application running with mock data.

## Switching to Your Backend API

### Step 1: Update Configuration

Open [src/services/api/index.ts](src/services/api/index.ts) and change line 12:

```typescript
const USE_MOCK_API = false; // Switch to your real API
```

### Step 2: Set API Base URL

Create a `.env` file:

```bash
VITE_API_BASE_URL=http://your-api-url.com/api
```

### Step 3: Customize Endpoints (if needed)

Open [src/services/api/realAdapter.ts](src/services/api/realAdapter.ts) and adjust the endpoints to match your API:

```typescript
// Example: Change endpoint URLs
async getMonitoredCourses(): Promise<MonitoredCourse[]> {
  const response = await this.client.get('/your-endpoint'); // ← Change this
  return this.transformMonitoredCoursesResponse(response.data);
}
```

### Step 4: Adjust Data Transformations (if needed)

If your API returns data in a different format, update the transformation methods in the same file:

```typescript
private transformMonitoredCourseResponse(data: any): MonitoredCourse {
  return {
    id: data._id,  // ← Map your fields
    term: data.semester,  // ← to frontend fields
    // ...
  };
}
```

## Expected API Endpoints

The frontend expects these endpoints (can be customized):

### Course Monitoring
```
GET    /monitors              - Get all monitored courses
POST   /monitors              - Add a course to monitor
PATCH  /monitors/:id          - Update a monitored course
DELETE /monitors/:id          - Remove a monitored course
GET    /monitors/:id/history  - Get enrollment history
```

### Notifications
```
GET  /preferences/notifications  - Get notification preferences
PUT  /preferences/notifications  - Update notification preferences
POST /notifications/test         - Test a notification
```

### Course Search (optional)
```
GET /courses/search?term=X&subject=Y&courseNumber=Z  - Search courses
GET /courses/:term/:subject/:courseNumber            - Get course details
```

## Data Models

All TypeScript interfaces are defined in [src/services/api/types.ts](src/services/api/types.ts).

Example of main interface:

```typescript
interface MonitoredCourse {
  id: string;
  term: string;
  subject: string;
  courseNumber: string;
  sections: string[];  // e.g., ["001", "002"]
  notifyOnOpen: boolean;
  notifyOnWaitlist: boolean;
  checkInterval: number;  // milliseconds
  active: boolean;
  lastChecked?: Date;
  createdAt: Date;
}
```

## Response Format Examples

### Adding a Monitored Course

**Request:**
```json
POST /monitors
{
  "term": "1252",
  "subject": "COMP SCI",
  "courseNumber": "400",
  "sections": ["001", "002"],
  "notifyOnOpen": true,
  "notifyOnWaitlist": false,
  "checkInterval": 300000,
  "active": true
}
```

**Response:**
```json
{
  "id": "abc123",
  "term": "1252",
  "subject": "COMP SCI",
  "courseNumber": "400",
  "sections": ["001", "002"],
  "notifyOnOpen": true,
  "notifyOnWaitlist": false,
  "checkInterval": 300000,
  "active": true,
  "createdAt": "2025-01-15T10:30:00Z",
  "lastChecked": null
}
```

## CORS Configuration

Make sure your backend allows requests from the frontend during development:

```
Access-Control-Allow-Origin: http://localhost:5173
Access-Control-Allow-Methods: GET, POST, PATCH, DELETE, PUT
Access-Control-Allow-Headers: Content-Type, Authorization
```

## Authentication (if needed)

The frontend is set up to handle JWT tokens. If your API requires authentication:

1. Store the token in localStorage after login
2. The frontend will automatically include it in all requests:

```typescript
// In realAdapter.ts (already implemented)
config.headers.Authorization = `Bearer ${token}`;
```

## Flexible Data Transformation

The adapter pattern includes transformation methods that can handle differences between your API format and the frontend's expected format:

```typescript
// Example: Your API uses snake_case, frontend uses camelCase
private transformMonitoredCourseResponse(data: any): MonitoredCourse {
  return {
    id: data.id,
    courseNumber: data.course_number,  // snake_case → camelCase
    notifyOnOpen: data.notify_on_open,
    // etc.
  };
}
```

This means:
- ✅ You don't need to change your backend to match the frontend
- ✅ The frontend doesn't need to change to match your backend
- ✅ The transformation layer handles all differences

## Testing the Integration

1. Make sure your backend is running
2. Set `USE_MOCK_API = false` in [src/services/api/index.ts](src/services/api/index.ts)
3. Set your API URL in `.env`
4. Run `npm run dev`
5. Open browser console to see API requests
6. Try adding a course - you should see the POST request to your backend

## Need Help?

Check these files for more details:
- [FRONTEND.md](FRONTEND.md) - Complete frontend documentation
- [src/services/api/types.ts](src/services/api/types.ts) - All TypeScript types
- [src/services/api/realAdapter.ts](src/services/api/realAdapter.ts) - API implementation
- [src/services/api/index.ts](src/services/api/index.ts) - Configuration

## Architecture Benefits

The adapter pattern provides:
- **Zero coupling** between frontend and backend
- **Easy testing** with mock data
- **Flexible integration** - adjust endpoints and data formats easily
- **Type safety** with TypeScript
- **Clear contract** defined in apiAdapter.ts
