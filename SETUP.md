# Setup Guide for IndoStar Naturals

This guide will help you get the IndoStar Naturals e-commerce platform up and running.

## Prerequisites Checklist

Before you begin, ensure you have the following installed:

- [ ] Python 3.11 or higher
- [ ] Node.js 18 or higher
- [ ] PostgreSQL 15 or higher
- [ ] Redis 7 or higher
- [ ] Docker and Docker Compose (recommended)
- [ ] Git

## Setup Steps

### Option 1: Docker Setup (Recommended)

This is the fastest way to get started.

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd indostar-naturals
   ```

2. **Configure environment variables**
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```

3. **Update backend/.env with your settings**
   - Set `JWT_SECRET_KEY` to a secure random string
   - Configure Razorpay credentials (get from https://razorpay.com)
   - Configure SMS provider (Twilio) credentials
   - Configure email provider (SendGrid) credentials
   - Configure S3 storage credentials

4. **Start all services**
   ```bash
   docker-compose up -d
   ```

5. **Initialize the database**
   ```bash
   docker-compose exec backend python scripts/init_db.py
   ```

6. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

7. **Login with default credentials**
   - Phone: +919999999999
   - Password: admin123
   - **⚠️ Change these immediately after first login!**

### Option 2: Local Development Setup

For development without Docker.

#### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Ensure PostgreSQL and Redis are running**
   ```bash
   # PostgreSQL should be running on localhost:5432
   # Redis should be running on localhost:6379
   ```

6. **Run migrations**
   ```bash
   alembic upgrade head
   ```

7. **Create initial owner account**
   ```bash
   python scripts/init_db.py
   ```

8. **Start the backend server**
   ```bash
   uvicorn app.main:app --reload
   ```

#### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Start the development server**
   ```bash
   npm run dev
   ```

## External Service Configuration

### Razorpay Setup

1. Sign up at https://razorpay.com
2. Get your API keys from the dashboard
3. Add keys to `backend/.env`:
   - `RAZORPAY_KEY_ID`
   - `RAZORPAY_KEY_SECRET`
   - `RAZORPAY_WEBHOOK_SECRET`
4. Add public key to `frontend/.env`:
   - `VITE_RAZORPAY_KEY_ID`

### SMS Provider (Twilio) Setup

1. Sign up at https://www.twilio.com
2. Get your credentials from the console
3. Add to `backend/.env`:
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `TWILIO_PHONE_NUMBER`

### Email Provider (SendGrid) Setup

1. Sign up at https://sendgrid.com
2. Create an API key
3. Add to `backend/.env`:
   - `SENDGRID_API_KEY`
   - `SENDGRID_FROM_EMAIL`

### S3 Storage Setup

1. Create an S3 bucket (AWS, DigitalOcean Spaces, etc.)
2. Create access credentials
3. Add to `backend/.env`:
   - `S3_BUCKET_NAME`
   - `S3_ACCESS_KEY`
   - `S3_SECRET_KEY`
   - `S3_REGION`
   - `S3_ENDPOINT_URL` (if not using AWS)
   - `CDN_BASE_URL` (optional)

### Google OAuth Setup (Optional)

1. Go to Google Cloud Console
2. Create OAuth 2.0 credentials
3. Add authorized redirect URIs
4. Add to `backend/.env`:
   - `GOOGLE_OAUTH_CLIENT_ID`
   - `GOOGLE_OAUTH_CLIENT_SECRET`

## Verification Steps

After setup, verify everything is working:

1. **Check backend health**
   ```bash
   curl http://localhost:8000/health
   ```
   Should return: `{"status": "healthy"}`

2. **Check database connection**
   ```bash
   docker-compose exec backend python -c "from app.core.database import engine; engine.connect()"
   ```

3. **Check Redis connection**
   ```bash
   docker-compose exec redis redis-cli ping
   ```
   Should return: `PONG`

4. **Access API documentation**
   Open http://localhost:8000/docs in your browser

5. **Access frontend**
   Open http://localhost:5173 in your browser

## Common Issues

### Port Already in Use

If ports 5432, 6379, 8000, or 5173 are already in use:

1. Stop conflicting services
2. Or modify ports in `docker-compose.yml` and `.env` files

### Database Connection Error

- Ensure PostgreSQL is running
- Check `DATABASE_URL` in `.env`
- Verify database exists: `psql -U postgres -l`

### Redis Connection Error

- Ensure Redis is running
- Check `REDIS_URL` in `.env`
- Test connection: `redis-cli ping`

### Migration Errors

If migrations fail:
```bash
# Reset database (⚠️ destroys all data)
docker-compose down -v
docker-compose up -d postgres
docker-compose exec backend alembic upgrade head
```

### Frontend Build Errors

If npm install fails:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Next Steps

After successful setup:

1. **Change default owner password**
   - Login with default credentials
   - Navigate to profile settings
   - Update password

2. **Configure email templates**
   - Customize notification templates
   - Test email delivery

3. **Upload product data**
   - Login as owner
   - Navigate to product management
   - Add categories and products

4. **Test payment flow**
   - Use Razorpay test mode
   - Create test orders
   - Verify webhook handling

5. **Set up monitoring**
   - Configure Sentry DSN
   - Test error reporting
   - Set up alerts

## Development Workflow

1. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes and test**
   ```bash
   # Backend tests
   cd backend && pytest
   
   # Frontend tests
   cd frontend && npm test
   ```

3. **Lint and format**
   ```bash
   make lint
   make format
   ```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin feature/your-feature-name
   ```

5. **Create pull request**
   - Open PR on GitHub
   - Wait for CI checks to pass
   - Request review

## Support

For issues or questions:
- Check the main README.md
- Review API documentation at /docs
- Open an issue on GitHub
- Contact the development team

## Security Notes

- Never commit `.env` files
- Use strong passwords in production
- Enable HTTPS in production
- Regularly update dependencies
- Monitor security advisories
- Implement rate limiting
- Use secure session management
- Validate all user inputs
- Sanitize outputs to prevent XSS
- Use parameterized queries to prevent SQL injection

## Production Deployment

See the main README.md for production deployment instructions.

Key considerations:
- Use production-grade database (RDS, managed PostgreSQL)
- Use Redis cluster for high availability
- Enable database backups
- Set up CDN for static assets
- Configure SSL certificates
- Set up monitoring and alerting
- Implement log aggregation
- Use secrets management (AWS Secrets Manager, etc.)
- Enable auto-scaling
- Set up disaster recovery plan
