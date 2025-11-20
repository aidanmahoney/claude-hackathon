# Quick Start Guide

## Running the Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

The frontend is fully functional with mock data!

## Project Structure

```
claude-hackathon/
├── frontend/                    # React + TypeScript frontend (✅ Complete)
│   ├── src/
│   │   ├── components/         # UI components
│   │   ├── services/api/       # API adapter layer
│   │   ├── App.tsx            # Main app
│   │   └── index.css          # Global styles
│   ├── public/                # Static assets
│   ├── README.md              # Frontend quick start
│   ├── FRONTEND.md            # Detailed guide
│   ├── INTEGRATION_GUIDE.md   # Backend integration
│   └── ARCHITECTURE.md        # Architecture docs
│
├── backend/                    # Backend (⏳ To be implemented)
│   └── (Place your backend code here)
│
├── README.md                   # Main project documentation
├── QUICK_START.md             # This file
└── .gitignore                 # Git ignore rules
```

## Current Status

✅ **Frontend**: Complete and functional
- Beautiful UI with dark theme
- Course monitoring dashboard
- Add/remove/pause courses
- Notification settings
- Mock API for development
- Ready for backend integration

⏳ **Backend**: Not yet implemented
- Will be in `backend/` directory
- Frontend ready to connect when ready

## For Frontend Development

```bash
cd frontend
npm install          # Install dependencies
npm run dev          # Start dev server
npm run build        # Build for production
```

## For Backend Integration

When the backend is ready:

1. **Switch to real API**:
   - Edit `frontend/src/services/api/index.ts`
   - Change `USE_MOCK_API = false`

2. **Configure API URL**:
   - Create `frontend/.env`
   - Set `VITE_API_BASE_URL=http://your-backend-url/api`

3. **Customize endpoints** (if needed):
   - Edit `frontend/src/services/api/realAdapter.ts`
   - Adjust endpoint URLs to match your backend
   - Update data transformations if needed

See [frontend/INTEGRATION_GUIDE.md](frontend/INTEGRATION_GUIDE.md) for complete instructions.

## Key Features

### Frontend
- 📊 Dashboard for monitoring multiple courses
- ➕ Add courses with custom check intervals
- ⏸️ Pause/resume monitoring
- 🔔 Configure email, SMS, webhook notifications
- 📱 Responsive design (mobile + desktop)
- 🌙 Modern dark theme
- 🔧 Mock API for development

### Backend (To be implemented)
- API endpoints for course management
- Database for storing course data
- Scheduler for polling UW Madison API
- Notification service (email, SMS, webhooks)
- Enrollment history tracking

## API Integration Pattern

The frontend uses an **adapter pattern** for maximum flexibility:

```
Components → API Service → [Mock Adapter | Real Adapter]
```

Benefits:
- ✅ Frontend works immediately (mock data)
- ✅ Easy to switch to real backend (one line change)
- ✅ Flexible endpoint configuration
- ✅ Data transformation layer handles format differences
- ✅ Zero coupling between frontend and backend

## Documentation

- **[README.md](README.md)** - Project overview and architecture
- **[frontend/README.md](frontend/README.md)** - Frontend quick start
- **[frontend/FRONTEND.md](frontend/FRONTEND.md)** - Complete frontend guide
- **[frontend/INTEGRATION_GUIDE.md](frontend/INTEGRATION_GUIDE.md)** - Backend integration
- **[frontend/ARCHITECTURE.md](frontend/ARCHITECTURE.md)** - Architecture details

## Next Steps

1. ✅ Frontend is done - run it and explore!
2. ⏳ Implement backend in `backend/` directory
3. ⏳ Connect frontend to backend (one line change)
4. ⏳ Deploy and test

## Need Help?

- Check the documentation in `frontend/`
- Review the API types in `frontend/src/services/api/types.ts`
- See example endpoints in `frontend/src/services/api/realAdapter.ts`
- Look at the mock implementation in `frontend/src/services/api/mockAdapter.ts`

The frontend is designed to be **moldable** - it can easily adapt to whatever backend API you create!
