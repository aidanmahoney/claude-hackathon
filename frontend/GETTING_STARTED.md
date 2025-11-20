# Getting Started with the Frontend

## Installation

```bash
npm install
```

## Development

```bash
npm run dev
```

The app will start at [http://localhost:5173](http://localhost:5173)

## What You'll See

### Empty State
When you first open the app, you'll see:
- A clean dashboard with no courses
- An "Add Course" button
- Two tabs: "Monitored Courses" and "Notification Settings"

### Adding Your First Course

1. Click "Add Course to Monitor"
2. Fill in the form:
   - **Term**: e.g., `1252` (Spring 2025)
   - **Subject**: e.g., `COMP SCI`
   - **Course Number**: e.g., `400`
   - **Sections**: e.g., `001, 002` (comma-separated)
   - **Check Interval**: How often to check (3, 5, 10, or 15 minutes)
   - **Notifications**: Toggle what you want to be notified about
3. Click "Add Course"

### Managing Courses

Each course card shows:
- Course name (subject + number)
- Term and sections
- Active/Paused status
- Check interval and last checked time
- Notification preferences
- Pause/Resume button
- Remove button

### Setting Up Notifications

Click the "Notification Settings" tab to configure:
- **Email**: Enter your email and test it
- **SMS**: Enter your phone number and test it
- **Webhook**: Enter your webhook URL and test it

## Using Mock Data

The app currently uses **mock data** which means:
- All actions work in the UI
- Data is stored in memory (resets on refresh)
- No real API calls are made
- Perfect for testing and development

## Switching to Real API

When your backend is ready:

1. Open `src/services/api/index.ts`
2. Change line 12:
   ```typescript
   const USE_MOCK_API = false;
   ```
3. Create a `.env` file:
   ```bash
   VITE_API_BASE_URL=http://localhost:3000/api
   ```
4. Restart the dev server

## Building for Production

```bash
npm run build
```

Output will be in the `dist/` directory.

## Project Features

✅ **Currently Working** (with mock data):
- Add/remove courses
- Pause/resume monitoring
- Update notification preferences
- Toast notifications for feedback
- Responsive design
- Dark theme

⏳ **Requires Backend**:
- Actual course monitoring
- Real notifications (email, SMS, webhook)
- Enrollment history
- Data persistence

## File Structure

```
src/
├── components/
│   ├── CourseCard.tsx          # Individual course card
│   ├── AddCourseModal.tsx      # Modal for adding courses
│   └── NotificationSettings.tsx # Notification config
│
├── services/api/
│   ├── types.ts                # TypeScript interfaces
│   ├── apiAdapter.ts           # API contract
│   ├── mockAdapter.ts          # Mock implementation (current)
│   ├── realAdapter.ts          # Real API (for backend)
│   └── index.ts                # Config (switch mock/real)
│
├── App.tsx                     # Main application
├── index.css                   # Global styles
└── main.tsx                    # Entry point
```

## Common Tasks

### Change Theme Colors
Edit `src/index.css` - look for color values like `#3b82f6` (blue), `#10b981` (green), etc.

### Modify Form Fields
Edit `src/components/AddCourseModal.tsx`

### Add New API Endpoints
1. Add method to interface in `src/services/api/apiAdapter.ts`
2. Implement in `src/services/api/mockAdapter.ts` (for testing)
3. Implement in `src/services/api/realAdapter.ts` (for production)

### Change Check Intervals
Edit the `<select>` options in `src/components/AddCourseModal.tsx` (line ~110)

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 5173
lsof -ti:5173 | xargs kill -9
```

### Type Errors
```bash
# Clear TypeScript cache
rm -rf node_modules/.vite
npm run dev
```

### Module Not Found
```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

## Next Steps

1. ✅ Explore the UI with mock data
2. ✅ Read the integration guide ([INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md))
3. ⏳ Implement your backend
4. ⏳ Switch to real API
5. ⏳ Deploy!

## Documentation

- **[README.md](README.md)** - Overview and quick start
- **[FRONTEND.md](FRONTEND.md)** - Complete frontend guide
- **[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** - Backend integration
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Architecture details
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - This file

Happy coding! 🚀
