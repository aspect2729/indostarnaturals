"""FastAPI Application Entry Point"""
import logging
import warnings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging_config import configure_logging
from app.core.security_middleware import add_security_middleware
from app.core.error_handlers import add_exception_handlers
from app.core.request_id_middleware import RequestIDMiddleware
from app.api import auth, users, products, owner_products, cart, webhooks, orders, owner_orders, subscriptions, owner_subscriptions, distributors, bulk_discounts, analytics, owner_users, admin_migrations

# Suppress pkg_resources deprecation warning from razorpay
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pkg_resources")

# Configure structured logging
configure_logging()
logger = logging.getLogger(__name__)

# Import monitoring after logging is configured
from app.core.monitoring import setup_sentry_custom_metrics

app = FastAPI(
    title="IndoStar Naturals API",
    description="E-commerce platform for organic jaggery, milk, and milk products",
    version="1.0.0",
)

logger.info("IndoStar Naturals API starting up", extra={"environment": settings.ENVIRONMENT})

# Setup monitoring and custom metrics
setup_sentry_custom_metrics()

# Request ID Middleware (must be added first to track all requests)
app.add_middleware(RequestIDMiddleware)

# Security Middleware (input sanitization and security headers)
add_security_middleware(app)

# Exception Handlers (standardized error responses)
add_exception_handlers(app)

# CORS Configuration
# Allow multiple frontend origins for development and production
allowed_origins = [
    "http://localhost:5173",  # Local Vite dev server
    "http://localhost:5174",  # Alternative local port
    "http://localhost:3000",  # Alternative local port
]

# Add production frontend URL if configured
if settings.FRONTEND_URL:
    allowed_origins.append(settings.FRONTEND_URL)

# Add Vercel deployment URLs
allowed_origins.extend([
    "https://indostarnaturals.vercel.app",
    "https://indostarnaturals-git-main.vercel.app",  # Git branch deployments
])

logger.info(f"CORS allowed origins: {allowed_origins}")

# For Vercel preview deployments, we need to allow origin pattern matching
from fastapi.middleware.cors import CORSMiddleware as BaseCORSMiddleware

def is_allowed_origin(origin: str) -> bool:
    """Check if origin is allowed, including Vercel preview deployments"""
    if origin in allowed_origins:
        return True
    # Allow all Vercel preview deployments for this project
    if origin.startswith("https://indostarnaturals-") and origin.endswith(".vercel.app"):
        return True
    return False

# Custom CORS middleware that handles Vercel preview URLs
@app.middleware("http")
async def cors_middleware(request, call_next):
    from fastapi.responses import Response
    
    origin = request.headers.get("origin")
    
    # Handle preflight requests
    if request.method == "OPTIONS" and origin and is_allowed_origin(origin):
        return Response(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Max-Age": "3600",
            }
        )
    
    response = await call_next(request)
    
    if origin and is_allowed_origin(origin):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Expose-Headers"] = "*"
    
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(owner_products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(owner_orders.router)
app.include_router(subscriptions.router)
app.include_router(owner_subscriptions.router)
app.include_router(distributors.router)
app.include_router(bulk_discounts.router)
app.include_router(analytics.router)
app.include_router(owner_users.router)
app.include_router(webhooks.router)
app.include_router(admin_migrations.router)  # Temporary - remove after deployment

# Test endpoints (development only)
if settings.ENVIRONMENT == "development":
    from app.api import test_auth
    app.include_router(test_auth.router)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "IndoStar Naturals API", "status": "healthy"}


@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers"""
    from app.core.database import get_db
    from app.core.redis_client import is_redis_available
    
    health_status = {
        "status": "healthy",
        "timestamp": logging.Formatter().formatTime(logging.LogRecord("", 0, "", 0, "", (), None)),
        "services": {}
    }
    
    # Check database connectivity
    try:
        from sqlalchemy import text
        db = next(get_db())
        db.execute(text("SELECT 1"))
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        health_status["services"]["database"] = "unhealthy"
        health_status["status"] = "degraded"
        logger.error(f"Database health check failed: {str(e)}")
    
    # Check Redis connectivity (non-blocking)
    if is_redis_available():
        health_status["services"]["redis"] = "healthy"
    else:
        health_status["services"]["redis"] = "unhealthy"
        health_status["status"] = "degraded"
        logger.warning("Redis health check failed - service degraded but operational")
    
    return health_status
