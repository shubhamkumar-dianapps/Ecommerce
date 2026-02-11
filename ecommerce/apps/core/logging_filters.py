"""
Logging Filters

Custom logging filters to add contextual information to log records.
"""

import threading


# Thread-local storage for request ID
class RequestIDContext(threading.local):
    """Thread-local storage for the current request ID."""

    request_id = None


request_id_context = RequestIDContext()


class RequestIDFilter:
    """
    Logging filter that adds the request ID to log records.

    Usage in logging configuration:
        'filters': {
            'request_id': {
                '()': 'apps.core.logging_filters.RequestIDFilter',
            }
        }
    """

    def filter(self, record):
        """Add request_id to the log record."""
        record.request_id = getattr(request_id_context, "request_id", "-")
        return True
