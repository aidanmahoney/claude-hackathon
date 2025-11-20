# Testing Guide

## Frontend Persistence Testing

The frontend now includes **localStorage persistence** for the mock API, meaning your data will survive page refreshes!

### How to Test Persistence

#### 1. Start the Frontend

```bash
cd frontend
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

#### 2. Add a Course

1. Click "Add Course to Monitor"
2. Fill in the form:
   - Term: `1252`
   - Subject: `COMP SCI`
   - Course Number: `400`
   - Sections: `001, 002`
   - Check Interval: `5 minutes`
   - Enable "Notify when seats open"
3. Click "Add Course"

#### 3. Verify the Course Appears

You should see a card with:
- Course name: COMP SCI 400
- Status: Active
- Sections: 001, 002
- Check interval: 5 min

#### 4. Test Persistence

**Refresh the page** (press F5 or Cmd+R)

✅ **Expected Result**: The course you added should still be there!

The data is stored in your browser's localStorage, so it persists across:
- Page refreshes
- Browser tab closes/opens
- Navigating away and back

#### 5. Test Updating

1. Click "Pause Monitoring" on your course
2. Refresh the page
3. ✅ The course should still show as "Paused"

#### 6. Test Notification Settings

1. Click the "Notification Settings" tab
2. Enable email notifications
3. Enter an email address
4. Click "Save Preferences"
5. Refresh the page
6. ✅ Your email settings should still be there

#### 7. Test Deletion

1. Click the X button to remove a course
2. Refresh the page
3. ✅ The course should remain deleted

### What's Persisted

The mock API now persists to localStorage:
- ✅ All monitored courses
- ✅ Course settings (active/paused, intervals, sections)
- ✅ Notification preferences (email, SMS, webhook)

### Clearing Test Data

If you want to start fresh:

**Option 1: Clear from Browser DevTools**
1. Open DevTools (F12)
2. Go to Application tab (Chrome) or Storage tab (Firefox)
3. Find localStorage
4. Delete keys: `mockMonitoredCourses` and `mockNotificationPrefs`

**Option 2: Clear from Console**
```javascript
localStorage.removeItem('mockMonitoredCourses');
localStorage.removeItem('mockNotificationPrefs');
location.reload();
```

## Backend Testing

### Testing the Backend (When Python 3.9-3.12 is available)

The backend requires Python 3.9-3.12 due to pydantic compatibility issues with 3.13.

**If you have Python 3.9-3.12:**

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py --help
```

### Backend Features to Test

When the backend is running:

1. **Database Persistence**
   ```bash
   # The backend uses SQLite by default
   # Data is stored in: backend/data/courses.db
   ```

2. **API Endpoints**
   - The backend implements REST API endpoints
   - See [backend/README.md](backend/README.md) for details

3. **UW Courses API Integration**
   ```bash
   cd backend
   python test_api.py  # Test the UW Courses API
   ```

## Integration Testing (Frontend + Backend)

### Step 1: Start the Backend

```bash
cd backend
python main.py
# Backend runs on http://localhost:8000
```

### Step 2: Configure Frontend

Edit `frontend/src/services/api/index.ts`:
```typescript
const USE_MOCK_API = false; // Switch to real API
```

Create `frontend/.env`:
```bash
VITE_API_BASE_URL=http://localhost:8000/api
```

### Step 3: Start the Frontend

```bash
cd frontend
npm run dev
# Frontend runs on http://localhost:5173
```

### Step 4: Test End-to-End

1. Add a course in the UI
2. The data should be sent to the backend
3. Check the database: `backend/data/courses.db`
4. Stop and restart the backend
5. Refresh the frontend
6. ✅ The course should still be there (persisted in database)

## Test Scenarios

### Scenario 1: Basic CRUD Operations

✅ **Create**: Add a new course
✅ **Read**: View all courses
✅ **Update**: Pause/resume a course
✅ **Delete**: Remove a course

### Scenario 2: Persistence Across Sessions

1. Add 3 courses
2. Close browser
3. Open browser again
4. Navigate to the app
5. ✅ All 3 courses should be there

### Scenario 3: Notification Settings

1. Configure email notifications
2. Enable SMS with a phone number
3. Add a webhook URL
4. Save settings
5. Refresh page
6. ✅ All settings should be preserved

### Scenario 4: Multiple Courses

1. Add courses from different subjects (COMP SCI, MATH, ENGLISH)
2. Set different check intervals for each
3. Pause some, leave others active
4. Refresh page
5. ✅ All courses should maintain their individual settings

## Known Limitations

### Mock API (Current)
- ✅ Data persists in browser localStorage
- ❌ No real-time course monitoring
- ❌ No actual notifications sent
- ❌ Enrollment history is randomly generated
- ❌ Data only persists in the same browser

### Backend API (When Integrated)
- ✅ Real database persistence (SQLite/PostgreSQL)
- ✅ Actual course monitoring from UW API
- ✅ Real email/SMS notifications
- ✅ Accurate enrollment history
- ✅ Data persists across devices

## Troubleshooting

### Frontend not saving data?

Check browser console for errors:
```javascript
// Test localStorage manually
localStorage.setItem('test', 'hello');
console.log(localStorage.getItem('test')); // Should show 'hello'
```

If localStorage is disabled (private browsing), the app will still work but won't persist data.

### Backend won't start?

Check Python version:
```bash
python3 --version  # Should be 3.9, 3.10, 3.11, or 3.12
```

If you have Python 3.13, you'll need to use Docker or install Python 3.12 separately.

### Frontend can't connect to backend?

1. Check backend is running: `curl http://localhost:8000`
2. Check CORS is enabled in backend
3. Verify `.env` has correct `VITE_API_BASE_URL`
4. Check browser console for errors

## Success Criteria

✅ Frontend builds without errors
✅ Frontend runs and displays UI correctly
✅ Can add courses and they appear in the list
✅ Data persists after page refresh
✅ Can pause/resume courses
✅ Can delete courses
✅ Notification settings can be saved and persist
✅ No console errors in normal operation

## Next Steps

Once both frontend and backend are fully integrated and tested:

1. Deploy frontend to Vercel/Netlify
2. Deploy backend to Heroku/Railway/Render
3. Set up production database (PostgreSQL)
4. Configure real email/SMS services
5. Set up monitoring and logging
6. Implement user authentication (if needed)
