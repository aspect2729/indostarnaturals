"""Redis client configuration"""
import redis
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# Create Redis client (lazy connection - will connect on first use)
redis_client = None
redis_available = False

# Try to initialize Redis if URL is provided
if settings.REDIS_URL and settings.REDIS_URL != "redis://localhost:6379":
    try:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=10,
            socket_timeout=10,
            socket_keepalive=True,
            ssl_cert_reqs=None,
            retry_on_timeout=True,
            max_connections=10,
        )
        logger.info(f"Redis client created with URL: {settings.REDIS_URL[:30]}...")
        
        # Test connection
        redis_client.ping()
        redis_available = True
        logger.info("✅ Redis connected successfully - caching enabled")
        
    except redis.exceptions.ConnectionError as e:
        logger.warning(f"⚠️ Redis connection failed: {e}")
        logger.warning("App will run without Redis caching")
        redis_client = None
        redis_available = False
        
    except redis.exceptions.AuthenticationError as e:
        logger.error(f"❌ Redis authentication failed: {e}")
        logger.error("Check your REDIS_URL password")
        redis_client = None
        redis_available = False
        
    except Exception as e:
        logger.warning(f"⚠️ Redis initialization failed: {e}")
        logger.warning("App will run without Redis caching")
        redis_client = None
        redis_available = False
else:
    logger.info("ℹ️ Redis not configured (REDIS_URL not set)")


def get_redis():
    """
    Get Redis client instance.
    Returns None if Redis is not available.
    """
    if not redis_available or redis_client is None:
        return None
    
    try:
        redis_client.ping()
        return redis_client
    except Exception as e:
        logger.warning(f"Redis ping failed: {e}")
        return None


def is_redis_available() -> bool:
    """Check if Redis is available"""
    if not redis_available or redis_client is None:
        return False
    try:
        redis_client.ping()
        return True
    except Exception:
        return False
