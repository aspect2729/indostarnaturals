# Deploying to Vercel (Frontend) and Render (Backend)

This guide walks you through deploying your IndoStar Naturals e-commerce application with the frontend on Vercel and backend on Render.

## Prerequisites

- GitHub account with your repository
- Vercel account (vercel.com)
- Render account (render.com)
- Domain name (optional, but recommended)

## Part 1: Deploy Backend to Render

### 1.1 Create PostgreSQL Database

1. Go to Render Dashboard → New → PostgreSQL
2. Name: `indostar-naturals-db`
3. Database: `indostar_naturals`
4. User: `indostar_user`
5. Region: Choose closest to your users
6. Plan: Free (or paid for production)
7. Click "Create Database"
8. **Save the Internal Database URL** (starts with `postgresql://`)

### 1.2 Create Redis Instance

1. Go to Render Dashboard → New → Redis
2. Name: `indostar-naturals-redis`
3. Region: Same as database
4. Plan: Free (or paid for production)
5. Click "Create Redis"
6. **Save the Internal Redis URL** (starts with `redis://`)

### 1.3 Deploy Backend Web Service

1. Go to Render Dashboard → New → Web Service
2. Connect your GitHub repository
3. Configure:
   - **Name**: `indostar-naturals-backend`
   - **Region**: Same as database
   - **Branch**: `master` (or `main`)
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free (or paid for production)

4. Add Environment Variables (click "Advanced" → "Add Environment Variable"):

```bash
# Database
DATABASE_URL=<your-postgres-internal-url-from-step-1.1>

# Redis
REDIS_URL=<your-redis-internal-url-from-step-1.2>

# Security
JWT_SECRET_KEY=<generate-a-secure-random-string>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Razorpay (get from razorpay.com dashboard)
RAZORPAY_KEY_ID=<your-razorpay-key-id>
RAZORPAY_KEY_SECRET=<your-razorpay-key-secret>
RAZORPAY_WEBHOOK_SECRET=<your-razorpay-webhook-secret>

# Twilio (get from twilio.com console)
SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=<your-twilio-account-sid>
TWILIO_AUTH_TOKEN=<your-twilio-auth-token>
TWILIO_PHONE_NUMBER=<your-twilio-phone-number>

# Email (get from sendgrid.com)
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=<your-sendgrid-api-key>
SENDGRID_FROM_EMAIL=noreply@yourdomain.com

# Google OAuth (get from console.cloud.google.com)
GOOGLE_OAUTH_CLIENT_ID=<your-google-client-id>
GOOGLE_OAUTH_CLIENT_SECRET=<your-google-client-secret>

# AWS S3 (for image uploads)
S3_BUCKET_NAME=<your-s3-bucket-name>
S3_ACCESS_KEY=<your-aws-access-key>
S3_SECRET_KEY=<your-aws-secret-key>
S3_REGION=us-east-1
S3_ENDPOINT_URL=https://s3.amazonaws.com
CDN_BASE_URL=https://cdn.yourdomain.com

# Application URLs (IMPORTANT: Update after Vercel deployment)
FRONTEND_URL=https://your-app.vercel.app
BACKEND_URL=https://indostar-naturals-backend.onrender.com
ENVIRONMENT=production
```

5. Click "Create Web Service"
6. Wait for deployment to complete
7. **Save your backend URL**: `https://indostar-naturals-backend.onrender.com`

### 1.4 Run Database Migrations

After deployment, run migrations:

1. Go to your Render service → Shell
2. Run:
```bash
alembic upgrade head
```

3. Create initial owner account:
```bash
python -c "from app.models.user import User; from app.core.database import SessionLocal; from app.core.security import get_password_hash; db = SessionLocal(); owner = User(name='Owner', email='owner@indostarnaturals.com', phone='+919876543210', password_hash=get_password_hash('ChangeMe123!'), role='owner', is_active=True); db.add(owner); db.commit(); print('Owner created')"
```

## Part 2: Deploy Frontend to Vercel

### 2.1 Prepare Frontend

1. Update `frontend/.env.production`:
```env
VITE_API_BASE_URL=https://indostar-naturals-backend.onrender.com
```

2. Commit and push to GitHub

### 2.2 Deploy to Vercel

1. Go to vercel.com → New Project
2. Import your GitHub repository
3. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

4. Add Environment Variable:
   - **Name**: `VITE_API_BASE_URL`
   - **Value**: `https://indostar-naturals-backend.onrender.com`

5. Click "Deploy"
6. Wait for deployment
7. **Save your Vercel URL**: `https://your-app.vercel.app`

### 2.3 Update Backend CORS

1. Go back to Render → Your Backend Service → Environment
2. Update `FRONTEND_URL` to your Vercel URL:
```
FRONTEND_URL=https://your-app.vercel.app
```
3. Save and redeploy

## Part 3: Configure External Services

### 3.1 Update Google OAuth

1. Go to Google Cloud Console → APIs & Services → Credentials
2. Edit your OAuth 2.0 Client ID
3. Add Authorized JavaScript origins:
   - `https://your-app.vercel.app`
4. Add Authorized redirect URIs:
   - `https://your-app.vercel.app`
   - `https://your-app.vercel.app/auth/callback`
5. Save

### 3.2 Update Razorpay Webhooks

1. Go to Razorpay Dashboard → Settings → Webhooks
2. Add webhook URL:
   - `https://indostar-naturals-backend.onrender.com/api/v1/webhooks/razorpay`
3. Select events: `payment.captured`, `subscription.charged`, etc.
4. Save

### 3.3 Configure Custom Domain (Optional)

**For Vercel:**
1. Go to your project → Settings → Domains
2. Add your domain (e.g., `indostarnaturals.com`)
3. Follow DNS configuration instructions

**For Render:**
1. Go to your service → Settings → Custom Domain
2. Add your API subdomain (e.g., `api.indostarnaturals.com`)
3. Follow DNS configuration instructions

## Part 4: Testing

### 4.1 Test Backend

Visit: `https://indostar-naturals-backend.onrender.com/health`

Should return:
```json
{
  "status": "healthy",
  "services": {
    "database": "healthy",
    "redis": "healthy"
  }
}
```

### 4.2 Test Frontend

1. Visit: `https://your-app.vercel.app`
2. Open browser DevTools → Network tab
3. Try to browse products
4. Check API calls go to your Render backend
5. Verify no CORS errors

### 4.3 Test Authentication

1. Try to register a new user
2. Try to login
3. Check OTP flow works
4. Test Google OAuth

## Part 5: Monitoring & Maintenance

### 5.1 Set Up Monitoring

**Render:**
- Enable auto-deploy on push
- Set up health check alerts
- Monitor logs in dashboard

**Vercel:**
- Enable auto-deploy on push
- Monitor analytics
- Set up error tracking

### 5.2 Database Backups

Render automatically backs up PostgreSQL databases. To manually backup:

1. Go to your database → Backups
2. Click "Create Backup"
3. Download if needed

### 5.3 Environment Variables Management

**Never commit sensitive data!**

- Use Render/Vercel dashboards for secrets
- Keep `.env.example` updated for reference
- Document all required variables

## Troubleshooting

### CORS Errors

- Verify `FRONTEND_URL` in Render matches your Vercel URL exactly
- Check CORS configuration in `backend/app/main.py`
- Ensure no trailing slashes in URLs

### Database Connection Issues

- Verify `DATABASE_URL` is the internal URL from Render
- Check database is in same region as backend
- Run migrations: `alembic upgrade head`

### Redis Connection Issues

- Verify `REDIS_URL` is the internal URL from Render
- Check Redis is in same region as backend
- Test connection in Render shell: `redis-cli ping`

### Build Failures

**Backend:**
- Check `requirements.txt` is up to date
- Verify Python version compatibility
- Check logs in Render dashboard

**Frontend:**
- Check `package.json` dependencies
- Verify Node version in Vercel settings
- Check build logs in Vercel dashboard

### API Not Responding

- Check backend service is running in Render
- Verify health endpoint works
- Check environment variables are set
- Review logs for errors

## Cost Optimization

### Free Tier Limits

**Render Free Tier:**
- Web services spin down after 15 minutes of inactivity
- 750 hours/month of runtime
- PostgreSQL: 1GB storage, 97 connection limit
- Redis: 25MB storage

**Vercel Free Tier:**
- 100GB bandwidth/month
- Unlimited deployments
- Automatic HTTPS

### Upgrade Recommendations

For production with real traffic:
- **Render**: Upgrade to Starter ($7/month) for always-on service
- **Database**: Upgrade for more storage and connections
- **Redis**: Upgrade for more memory
- **Vercel**: Pro plan ($20/month) for better performance

## Security Checklist

- [ ] All environment variables set correctly
- [ ] JWT_SECRET_KEY is strong and unique
- [ ] Database credentials are secure
- [ ] HTTPS enabled (automatic on Vercel/Render)
- [ ] CORS configured correctly
- [ ] API rate limiting enabled
- [ ] Input validation working
- [ ] Error messages don't expose sensitive data
- [ ] Logs don't contain secrets
- [ ] Google OAuth redirect URIs restricted
- [ ] Razorpay webhooks verified

## Next Steps

1. Set up monitoring (Sentry, LogRocket, etc.)
2. Configure CDN for static assets
3. Set up automated backups
4. Create staging environment
5. Set up CI/CD pipeline
6. Configure custom domains
7. Enable SSL certificates
8. Set up email notifications
9. Configure analytics
10. Create admin documentation

## Support

For issues:
- Check Render logs: Dashboard → Your Service → Logs
- Check Vercel logs: Dashboard → Your Project → Deployments → Logs
- Review this guide's troubleshooting section
- Check GitHub issues

## Resources

- [Render Documentation](https://render.com/docs)
- [Vercel Documentation](https://vercel.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Vite Deployment](https://vitejs.dev/guide/static-deploy.html)
