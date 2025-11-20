# Frontend Architecture

## API Adapter Pattern

The frontend uses an adapter pattern to create a flexible, moldable API layer that can easily switch between mock and real implementations.

```
┌─────────────────────────────────────────────────────────────┐
│                      React Components                       │
│  (CourseCard, AddCourseModal, NotificationSettings, etc.)  │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ Uses
                        ▼
        ┌───────────────────────────────┐
        │      API Service (api)        │
        │   src/services/api/index.ts   │
        └───────────────┬───────────────┘
                        │
                        │ Exports instance of
                        │
        ┌───────────────▼───────────────┐
        │      ApiAdapter Interface     │
        │ (Defines the contract/methods)│
        └───────────────┬───────────────┘
                        │
                        │ Implemented by
                        │
           ┌────────────┴──────────────┐
           │                           │
           ▼                           ▼
┌──────────────────────┐    ┌──────────────────────┐
│   MockApiAdapter     │    │   RealApiAdapter     │
│ (Development/Testing)│    │  (Production Use)    │
│                      │    │                      │
│  • Returns fake data │    │  • Calls backend API │
│  • Simulates delays  │    │  • Transforms data   │
│  • No backend needed │    │  • Handles auth      │
└──────────────────────┘    └──────────────────────┘
```

## Data Flow

### Example: Adding a Monitored Course

```
User clicks "Add Course"
        │
        ▼
AddCourseModal component
        │
        │ onAdd(courseData)
        ▼
App component
        │
        │ api.addMonitoredCourse(courseData)
        ▼
API Service (index.ts)
        │
        │ Routes to current adapter
        │
        ├─── USE_MOCK_API = true ──┐
        │                           ▼
        │                  MockApiAdapter
        │                  • Generates mock ID
        │                  • Returns fake data
        │
        └─── USE_MOCK_API = false ─┐
                                    ▼
                           RealApiAdapter
                           • POST /monitors
                           • Transforms response
                           • Returns MonitoredCourse
```

## Key Benefits

### 1. Zero Coupling
Components don't care about the API implementation. They just call methods on the `api` object.

### 2. Easy Switching
```typescript
// In src/services/api/index.ts
const USE_MOCK_API = true;  // Use mock data
const USE_MOCK_API = false; // Use real API
```

### 3. Moldable to Any Backend
```typescript
// In realAdapter.ts
async getMonitoredCourses(): Promise<MonitoredCourse[]> {
  // Change endpoint to match your backend
  const response = await this.client.get('/your-endpoint');
  
  // Transform data to match frontend expectations
  return this.transformMonitoredCoursesResponse(response.data);
}
```

### 4. Type Safety
All data types are defined in `types.ts`:
```typescript
interface MonitoredCourse {
  id: string;
  term: string;
  subject: string;
  courseNumber: string;
  sections: string[];
  // ...
}
```

## Component Structure

```
App.tsx (Main container)
├─ Header
├─ Tabs (Courses | Notifications)
├─ Course Tab
│  ├─ Action Buttons (Add, Refresh)
│  ├─ Active Courses Section
│  │  └─ CourseCard (for each course)
│  └─ Paused Courses Section
│     └─ CourseCard (for each course)
├─ Notification Tab
│  └─ NotificationSettings
│     ├─ Email Settings
│     ├─ SMS Settings
│     └─ Webhook Settings
└─ AddCourseModal (conditional)
```

## State Management

Currently using React's built-in `useState` and `useEffect` hooks:

- **App.tsx** manages:
  - List of monitored courses
  - Active tab
  - Loading states
  - Modal visibility

- **NotificationSettings** manages:
  - Notification preferences
  - Individual setting states

This is sufficient for the current complexity. Can easily add Redux or Zustand if needed.

## Styling Approach

Using inline styles and CSS classes:
- Global styles in `index.css`
- Component-specific styles inline
- Class-based styling for reusable patterns (`.card`, `.badge`, etc.)

Benefits:
- No CSS module complexity
- Easy to understand
- Fast to develop
- Can migrate to styled-components/Tailwind later if needed

## Future Enhancements

Potential improvements that maintain the flexible architecture:

1. **Add Redux/Zustand** - For complex state management
2. **Add React Query** - For better API state management and caching
3. **Add Tailwind CSS** - For more systematic styling
4. **Add Testing** - Jest + React Testing Library
5. **Add Storybook** - For component documentation
6. **Add Real-time Updates** - WebSocket support in adapter

All of these can be added without changing the core adapter pattern!
