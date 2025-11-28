"""Redis client configuration"""
import redis
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# Create Redis client (lazy connection - will connect on first use)
redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
)


def get_redis():
    """
    Get Redis client instance.
    Tests connection on each call to ensure Redis is available.
    """
    try:
        # Test connection
        redis_client.ping()
        return redis_client
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        raise ConnectionError("Redis is not available. Please ensure Redis server is running. See REDIS_SETUP_GUIDE.md for instructions.")


def is_redis_available() -> bool:
    """Check if Redis is available"""
    try:
        redis_client.ping()
        return True
    except Exception:
        return False
