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
from app.api import auth, users, products, owner_products, cart, webhooks, orders, owner_orders, subscriptions, owner_subscriptions, distributors, bulk_discounts, analytics, owner_users

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
# Allow multiple frontend origins for development
allowed_origins = [
    settings.FRONTEND_URL,
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "IndoStar Naturals API", "status": "healthy"}


@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers"""
    from app.core.database import get_db
    from app.core.redis_client import get_redis
    
    health_status = {
        "status": "healthy",
        "timestamp": logging.Formatter().formatTime(logging.LogRecord("", 0, "", 0, "", (), None)),
        "services": {}
    }
    
    # Check database connectivity
    try:
        db = next(get_db())
        db.execute("SELECT 1")
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        health_status["services"]["database"] = "unhealthy"
        health_status["status"] = "degraded"
        logger.error(f"Database health check failed: {str(e)}")
    
    # Check Redis connectivity
    try:
        redis_client = get_redis()
        redis_client.ping()
        health_status["services"]["redis"] = "healthy"
    except Exception as e:
        health_status["services"]["redis"] = "unhealthy"
        health_status["status"] = "degraded"
        logger.error(f"Redis health check failed: {str(e)}")
    
    return health_status
