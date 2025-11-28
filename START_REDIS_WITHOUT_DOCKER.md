# Start Redis Without Docker

Docker Desktop is not running on your machine. Here are your options:

## Option 1: Start Docker Desktop (Recommended)

1. **Open Docker Desktop** from your Start Menu
2. **Wait** for it to fully start (you'll see the Docker icon in your system tray)
3. **Then run**:
   ```powershell
   docker run -d -p 6379:6379 --name redis redis:7-alpine
   ```

## Option 2: Use Development Mode (No Redis Needed)

For testing Twilio OTP without Redis, you can use development mode:

### Update your `.env` file:

```env
# Change SMS_PROVIDER to development
SMS_PROVIDER=development
```

This will:
- Print OTPs to the console instead of sending SMS
- Skip Redis storage (OTPs stored in memory)
- Perfect for testing Twilio credentials

### Test it:

```powershell
cd backend
python test_twilio_otp.py
```

## Option 3: Install Redis for Windows

1. **Download Redis for Windows**:
   - Go to: https://github.com/microsoftarchive/redis/releases
   - Download: `Redis-x64-3.0.504.msi`

2. **Install it** (use default settings)

3. **Start Redis**:
   ```powershell
   redis-server
   ```

4. **Test it**:
   ```powershell
   redis-cli ping
   # Should return: PONG
   ```

## Option 4: Use WSL (Windows Subsystem for Linux)

If you have WSL installed:

```powershell
# Start WSL
wsl

# Install Redis (if not installed)
sudo apt-get update
sudo apt-get install redis-server

# Start Redis
sudo service redis-server start

# Test it
redis-cli ping
# Should return: PONG

# Exit WSL
exit
```

## Quick Test - Which Option to Choose?

### For Quick Testing (5 minutes):
✅ **Use Option 2 (Development Mode)**
- No Redis needed
- Tests Twilio credentials
- OTPs print to console

### For Full Testing (10 minutes):
✅ **Use Option 1 (Docker Desktop)**
- Most reliable
- Easy to start/stop
- Same as production

### For Production Setup:
✅ **Use Option 1 (Docker Desktop)** or **Option 4 (WSL)**

## Recommended: Development Mode for Now

Since you want to test Twilio OTP quickly, let's use development mode:

### Step 1: Update `.env`

Edit `backend/.env` and change:

```env
SMS_PROVIDER=development
```

### Step 2: Test Twilio

```powershell
cd backend
python test_twilio_otp.py
```

This will:
- ✅ Test your Twilio credentials
- ✅ Generate OTPs (printed to console)
- ✅ Skip Redis (not needed in dev mode)

### Step 3: See the OTP

When you run the test, you'll see:

```
[DEV] OTP for +919876543210: 123456
```

Copy that OTP and use it to verify!

## After Testing

Once you confirm Twilio works, you can:

1. **Start Docker Desktop**
2. **Run Redis**:
   ```powershell
   docker run -d -p 6379:6379 --name redis redis:7-alpine
   ```
3. **Change back to Twilio**:
   ```env
   SMS_PROVIDER=twilio
   ```

## Summary

**Right now, do this**:

1. Edit `backend/.env`:
   ```env
   SMS_PROVIDER=development
   ```

2. Test:
   ```powershell
   cd backend
   python test_twilio_otp.py
   ```

3. You should see all tests pass! ✅

**Later, when you want real SMS**:

1. Start Docker Desktop
2. Run: `docker run -d -p 6379:6379 --name redis redis:7-alpine`
3. Change `.env` back to: `SMS_PROVIDER=twilio`

---

**Need help?** The Twilio Account SID issue is already fixed, so development mode should work perfectly for testing!
