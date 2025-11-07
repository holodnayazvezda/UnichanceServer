import logging.config
import os

# Custom formatter that handles missing attributes in log records
class AccessLogFormatter(logging.Formatter):
    def format(self, record):
        # Add default values for attributes that might be missing
        if not hasattr(record, 'client_addr'):
            record.client_addr = '-'
        if not hasattr(record, 'request_line'):
            record.request_line = '-'
        if not hasattr(record, 'status_code'):
            record.status_code = '-'
        return super().format(record)

# Ensure logs directory exists
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,  # Keep default loggers like uvicorn
    "formatters": {
        "standard": {
            # Adjusted format for better readability
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "access": {
            # Specific format for access logs if needed, otherwise use standard
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(client_addr)s - \"%(request_line)s\" %(status_code)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            # Use custom formatter to handle missing attributes
            "()": "logging_config.AccessLogFormatter",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO", # Log INFO and above to console
            "stream": "ext://sys.stdout",  # Default is stderr
        },
        "file_app": {
            "class": "logging.handlers.RotatingFileHandler", # Use rotating file handler
            "filename": os.path.join(LOG_DIR, "app.log"),
            "formatter": "standard",
            "encoding": "utf-8",
            "level": "INFO", # Log INFO and above to app.log
            "maxBytes": 1024*1024*10, # 10 MB
            "backupCount": 5, # Keep 5 backup files
        },
         "file_access": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "access.log"),
            "formatter": "access", # Use access formatter
            "encoding": "utf-8",
            "level": "INFO", # Log INFO and above for access logs
            "maxBytes": 1024*1024*10, # 10 MB
            "backupCount": 5,
        },
         "file_error": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "error.log"),
            "formatter": "standard",
            "encoding": "utf-8",
            "level": "WARNING", # Log WARNING and above to error.log
            "maxBytes": 1024*1024*10, # 10 MB
            "backupCount": 5,
        },
    },
    "loggers": {
        # Root logger
        "": {
            "handlers": ["console", "file_app", "file_error"],
            "level": "INFO",
            "propagate": False # Prevent root logger messages going to other loggers
        },
        # Uvicorn access logger
        "uvicorn.access": {
            "handlers": ["console", "file_access"], # Use specific access handler
            "level": "INFO",
            "propagate": False # Don't propagate to root
        },
        # Uvicorn error logger
        "uvicorn.error": {
             "handlers": ["console", "file_app", "file_error"], # Log errors to console and app/error files
            "level": "INFO", # Capture INFO level errors from uvicorn as well
            "propagate": False
        },
        # FastAPI logger (if you use logger = logging.getLogger("fastapi"))
        "fastapi": {
            "handlers": ["console", "file_app", "file_error"],
            "level": "INFO",
            "propagate": False,
        },
         # APScheduler logger
        "apscheduler": {
            "handlers": ["console", "file_app", "file_error"],
            "level": "WARNING", # Reduce noise from scheduler unless it's a warning/error
            "propagate": False,
        },
        # Add other specific library loggers if needed
        "httpx": {
            "handlers": ["console", "file_app"],
            "level": "WARNING", # Log only warnings/errors from httpx
            "propagate": False,
        },
        "telethon": {
             "handlers": ["console", "file_app"],
             "level": "WARNING", # Log only warnings/errors from telethon
             "propagate": False,
        }
    },
}

def setup_logging():
    logging.config.dictConfig(LOGGING)
    logging.getLogger(__name__).info("Logging configured successfully.")