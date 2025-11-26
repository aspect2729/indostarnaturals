# IndoStar Naturals - Quick Start Guide

## Prerequisites

Ensure you have the following installed and running:
- ✅ PostgreSQL (running on port 5432)
- ✅ Redis (optional, for caching and background tasks)
- ✅ Python 3.12+
- ✅ Node.js 18+

## Quick Start (Windows)

### Option 1: Automated Start (Recommended)

Simply run the startup script:

```powershell
.\start-app.ps1
```

This will:
- Check if PostgreSQL and Redis are running
- Start the backend server on http://localhost:8000
- Start the frontend server on http://localhost:5173
- Open two terminal windows for monitoring

### Option 2: Manual Start

**Terminal 1 - Backend:**
```powershell
cd backend
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

## Access the Application

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

## Default Login Credentials

**Owner Account:**
- Phone: `+919876543210`
- OTP: Any 6 digits (in development mode)

## Stopping the Application

Press `Ctrl+C` in each terminal window, or run:

```powershell
.\stop-backend.ps1
```

## Troubleshooting

### Issue: "PostgreSQL is not running"
**Solution:** Start PostgreSQL service or run:
```powershell
.\setup-postgres.ps1
```

### Issue: "Port already in use"
**Solution:** Kill the process using the port:
```powershell
# For backend (port 8000)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# For frontend (port 5173)
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

### Issue: "Module not found" errors
**Solution:** Reinstall dependencies:
```powershell
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Issue: "Database connection failed"
**Solution:** Check your `.env` file and ensure PostgreSQL is running with correct credentials.

### Issue: "Redirect loop or stuck on products page"
**Solution:** Clear browser cache:
1. Open DevTools (F12)
2. Go to Application tab
3. Click "Clear storage"
4. Check all boxes and click "Clear site data"
5. Hard refresh (Ctrl+Shift+R)

Or navigate to: http://localhost:5173/clear-cache.html

## Features

- ✅ User authentication (Phone OTP)
- ✅ Product catalog with search and filters
- ✅ Shopping cart
- ✅ Order management
- ✅ Subscription management
- ✅ Role-based access (Owner, Distributor, Consumer)
- ✅ Payment integration (Razorpay)
- ✅ Admin dashboard
- ✅ Inventory management

## Development

### Running Tests

**Backend:**
```powershell
cd backend
pytest
```

**Frontend:**
```powershell
cd frontend
npm test
```

### Database Migrations

```powershell
cd backend
alembic upgrade head
```

## Support

For issues or questions, check:
- `SETUP.md` - Detailed setup instructions
- `backend/README.md` - Backend documentation
- `frontend/README.md` - Frontend documentation
- `docs/` - Additional documentation
