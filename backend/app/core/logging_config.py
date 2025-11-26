"""Structured Logging Configuration

Configures Python logging with JSON formatter for structured logs.
Integrates with Sentry for error tracking.
"""
import logging
import logging.config
import sys
import json
from datetime import datetime
from typing import Any, Dict
from pythonjsonlogger import jsonlogger
from app.core.config import settings


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter that adds standard fields to all log entries"""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]):
        """Add custom fields to log record"""
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp in ISO format
        if not log_record.get('timestamp'):
            log_record['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        
        # Add log level
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname
        
        # Add logger name
        log_record['logger'] = record.name
        
        # Add request_id if available (will be added by middleware)
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id
        
        # Add additional context fields
        if hasattr(record, 'user_id'):
            log_record['user_id'] = record.user_id
        
        if hasattr(record, 'method'):
            log_record['method'] = record.method
        
        if hasattr(record, 'path'):
            log_record['path'] = record.path
        
        if hasattr(record, 'status_code'):
            log_record['status_code'] = record.status_code
        
        if hasattr(record, 'duration'):
            log_record['duration'] = record.duration


def configure_logging():
    """Configure structured logging for the application"""
    
    # Determine log level from settings
    log_level = getattr(settings, 'LOG_LEVEL', 'INFO')
    
    # Create JSON formatter
    json_formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s',
        rename_fields={
            'levelname': 'level',
            'name': 'logger',
            'pathname': 'file',
            'lineno': 'line'
        }
    )
    
    # Configure handlers
    handlers = {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
            'stream': sys.stdout,
        }
    }
    
    # Add file handler if configured
    if hasattr(settings, 'LOG_FILE') and settings.LOG_FILE:
        handlers['file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'json',
            'filename': settings.LOG_FILE,
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
        }
    
    # Logging configuration
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'json': {
                '()': CustomJsonFormatter,
                'format': '%(timestamp)s %(level)s %(name)s %(message)s'
            }
        },
        'handlers': handlers,
        'root': {
            'level': log_level,
            'handlers': list(handlers.keys())
        },
        'loggers': {
            'app': {
                'level': log_level,
                'handlers': list(handlers.keys()),
                'propagate': False
            },
            'uvicorn': {
                'level': log_level,
                'handlers': list(handlers.keys()),
                'propagate': False
            },
            'uvicorn.access': {
                'level': log_level,
                'handlers': list(handlers.keys()),
                'propagate': False
            },
            'sqlalchemy.engine': {
                'level': 'WARNING',  # Only log warnings and errors from SQLAlchemy
                'handlers': list(handlers.keys()),
                'propagate': False
            }
        }
    }
    
    # Apply configuration
    logging.config.dictConfig(logging_config)
    
    # Configure Sentry if DSN is provided
    if hasattr(settings, 'SENTRY_DSN') and settings.SENTRY_DSN:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.logging import LoggingIntegration
            from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
            from sentry_sdk.integrations.redis import RedisIntegration
            
            # Configure Sentry integrations
            sentry_logging = LoggingIntegration(
                level=logging.INFO,  # Capture info and above as breadcrumbs
                event_level=logging.ERROR  # Send errors and above as events
            )
            
            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                environment=getattr(settings, 'ENVIRONMENT', 'production'),
                integrations=[
                    sentry_logging,
                    SqlalchemyIntegration(),
                    RedisIntegration(),
                ],
                traces_sample_rate=getattr(settings, 'SENTRY_TRACES_SAMPLE_RATE', 0.1),
                send_default_pii=False,  # Don't send PII by default
                before_send=before_send_sentry,
            )
            
            logging.info("Sentry error tracking initialized")
            
        except ImportError:
            logging.warning("Sentry SDK not installed. Error tracking disabled.")
        except Exception as e:
            logging.error(f"Failed to initialize Sentry: {str(e)}")


def before_send_sentry(event, hint):
    """
    Filter and modify events before sending to Sentry.
    Remove sensitive information and add custom context.
    """
    # Remove sensitive data from request body
    if 'request' in event and 'data' in event['request']:
        data = event['request']['data']
        if isinstance(data, dict):
            # Remove password fields
            for key in ['password', 'hashed_password', 'secret', 'token']:
                if key in data:
                    data[key] = '[REDACTED]'
    
    # Add custom tags
    if 'tags' not in event:
        event['tags'] = {}
    
    event['tags']['application'] = 'indostar-naturals'
    
    return event


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (typically __name__ of the module)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


# Initialize logging when module is imported
configure_logging()
