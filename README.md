# IndoStar Naturals E-Commerce Platform

A full-stack e-commerce platform for selling organic jaggery, milk, and milk products with role-based access control, subscription management, and integrated payment processing.

## Features

- **Multi-Role System**: Consumer, Distributor, and Owner roles with distinct permissions
- **Product Management**: Complete catalog management with dual pricing (consumer/distributor)
- **Shopping Cart**: Persistent cart with coupon support
- **Payment Processing**: Razorpay integration for payments and subscriptions
- **Subscription Service**: Recurring milk deliveries with flexible scheduling
- **Order Management**: Complete order lifecycle tracking
- **Audit Logging**: Comprehensive audit trail for all critical operations
- **Responsive Design**: Mobile-first design with Tailwind CSS

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15+
- **Cache**: Redis 7+
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Background Tasks**: Celery
- **Authentication**: JWT with bcrypt password hashing
- **Payment**: Razorpay API
- **Storage**: S3-compatible object storage

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Routing**: React Router
- **State Management**: React Query
- **Forms**: Formik + Yup
- **HTTP Client**: Axios

## Project Structure

```
indostar-naturals/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core configuration
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── tasks/          # Celery tasks
│   ├── alembic/            # Database migrations
│   ├── tests/              # Backend tests
│   └── scripts/            # Utility scripts
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Page components
│   │   ├── contexts/       # React contexts
│   │   ├── hooks/          # Custom hooks
│   │   ├── services/       # API services
│   │   └── utils/          # Utilities
│   └── public/             # Static assets
├── .github/                # GitHub Actions workflows
└── docker-compose.yml      # Docker composition
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Quick Start with Docker

1. Clone the repository:
```bash
git clone <repository-url>
cd indostar-naturals
```

2. Set up environment variables:
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

3. Update the `.env` files with your configuration

4. Start all services:
```bash
docker-compose up
```

5. Initialize the database:
```bash
docker-compose exec backend python scripts/init_db.py
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Local Development Setup

#### Backend Setup

1. Create a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run database migrations:
```bash
alembic upgrade head
```

5. Start the development server:
```bash
uvicorn app.main:app --reload
```

#### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start the development server:
```bash
npm run dev
```

## Default Credentials

After initializing the database, use these credentials to log in as the owner:

- **Phone**: +919999999999
- **Password**: admin123

⚠️ **IMPORTANT**: Change these credentials immediately after first login!

## Testing

### Backend Tests
```bash
cd backend
pytest                          # Run all tests
pytest --cov=app               # Run with coverage
pytest -m unit                 # Run unit tests only
pytest -m integration          # Run integration tests only
pytest -m property             # Run property-based tests only
```

### Frontend Tests
```bash
cd frontend
npm test                       # Run tests
npm run test:coverage          # Run with coverage
```

## Code Quality

### Backend
```bash
cd backend
black app/                     # Format code
flake8 app/                    # Lint code
mypy app/                      # Type checking
```

### Frontend
```bash
cd frontend
npm run lint                   # Lint code
npm run format                 # Format code
```

## Database Migrations

Create a new migration:
```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migration:
```bash
alembic downgrade -1
```

## Deployment

### Building for Production

#### Backend
```bash
cd backend
docker build -t indostar-backend:latest .
```

#### Frontend
```bash
cd frontend
npm run build
```

### Environment Variables

Ensure all required environment variables are set in production:

**Backend**:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `JWT_SECRET_KEY`: Secret key for JWT tokens
- `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`: Razorpay credentials
- `S3_BUCKET_NAME`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`: S3 storage credentials
- `SENTRY_DSN`: Error tracking (optional)

**Frontend**:
- `VITE_API_BASE_URL`: Backend API URL
- `VITE_RAZORPAY_KEY_ID`: Razorpay public key

## CI/CD

The project includes GitHub Actions workflows for:

- **Backend CI**: Linting, testing, and building backend
- **Frontend CI**: Linting, type checking, and building frontend
- **Deploy to Staging**: Automated deployment on main branch

Configure your deployment target in `.github/workflows/deploy-staging.yml`

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[API Documentation](docs/API.md)**: Complete API reference with examples
- **[Owner Admin Guide](docs/OWNER_GUIDE.md)**: Guide for managing the platform
- **[Deployment Guide](docs/DEPLOYMENT.md)**: Production deployment instructions
- **[Operations Runbook](docs/RUNBOOK.md)**: Troubleshooting and incident response
- **[Infrastructure Setup](terraform/README.md)**: Terraform infrastructure guide
- **[Monitoring Setup](monitoring/sentry-config.md)**: Sentry and CloudWatch configuration
- **[Logging Guide](monitoring/logging-config.md)**: Logging best practices

### Interactive API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Environment Variables

### Backend Environment Variables

See `backend/.env.example` for all available environment variables. Key variables include:

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `JWT_SECRET_KEY`: Secret key for JWT tokens (min 32 characters)
- `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`: Razorpay API credentials
- `S3_BUCKET_NAME`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`: S3 storage credentials
- `SENTRY_DSN`: Error tracking (optional but recommended)
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`: SMS service credentials
- `SENDGRID_API_KEY`: Email service credentials

### Frontend Environment Variables

See `frontend/.env.example` for all available environment variables. Key variables include:

- `VITE_API_BASE_URL`: Backend API URL
- `VITE_RAZORPAY_KEY_ID`: Razorpay public key for checkout

## Contributing

1. Create a feature branch from `develop`
2. Make your changes
3. Write tests for new functionality
4. Ensure all tests pass
5. Run linters and formatters
6. Submit a pull request

### Code Style

- **Backend**: Follow PEP 8, use Black for formatting
- **Frontend**: Follow Airbnb style guide, use Prettier for formatting

## License

[Your License Here]

## Support

### For Users
- **Email**: support@indostarnaturals.com
- **Documentation**: See `docs/OWNER_GUIDE.md`

### For Developers
- **Issues**: Open an issue on GitHub
- **Documentation**: See `docs/` directory
- **API Docs**: http://localhost:8000/docs

### For Operations
- **Runbook**: See `docs/RUNBOOK.md`
- **Deployment**: See `docs/DEPLOYMENT.md`
- **Monitoring**: See `monitoring/` directory
