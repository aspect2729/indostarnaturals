"""Redis client configuration"""
import redis
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# Create Redis client (lazy connection - will connect on first use)
# Support both redis:// and rediss:// (TLS) URLs
try:
    # Upstash requires longer timeouts and specific SSL settings
    redis_client = redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=30,  # Increased for Upstash
        socket_timeout=30,  # Increased for Upstash
        socket_keepalive=True,
        socket_keepalive_options={},
        ssl_cert_reqs=None,  # Don't verify SSL certificates for Upstash
        retry_on_timeout=True,
        retry_on_error=[redis.exceptions.ConnectionError, redis.exceptions.TimeoutError],
        health_check_interval=30,
        max_connections=10,
    )
    logger.info(f"Redis client initialized with URL: {settings.REDIS_URL[:20]}...")
except Exception as e:
    logger.error(f"Failed to create Redis client: {e}")
    redis_client = None


def get_redis():
    """
    Get Redis client instance.
    Tests connection on each call to ensure Redis is available.
    """
    if redis_client is None:
        logger.error("Redis client not initialized")
        raise ConnectionError("Redis is not available. Please ensure Redis server is running. See REDIS_SETUP_GUIDE.md for instructions.")
    
    try:
        # Test connection with timeout
        redis_client.ping()
        return redis_client
    except redis.exceptions.TimeoutError as e:
        logger.error(f"Redis connection timeout: {e}")
        raise ConnectionError("Redis connection timeout. The Redis server may be unreachable or overloaded.")
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        raise ConnectionError("Redis is not available. Please ensure Redis server is running. See REDIS_SETUP_GUIDE.md for instructions.")


def is_redis_available() -> bool:
    """Check if Redis is available"""
    if redis_client is None:
        return False
    try:
        redis_client.ping()
        return True
    except Exception:
        return False
