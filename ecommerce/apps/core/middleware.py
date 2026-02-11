"""
Request ID Middleware

Generates a unique ID for each request and adds it to the request object.
This ID can be used to trace a single request across multiple log files.
"""

import uuid
import logging
from django.utils.deprecation import MiddlewareMixin


class RequestIDMiddleware(MiddlewareMixin):
    """
    Middleware to generate and attach a unique request ID to each request.

    The request ID is:
    - Generated as a UUID4
    - Attached to the request object as request.id
    - Added to response headers as X-Request-ID
    - Available in logs via the RequestIDFilter
    """

    def process_request(self, request):
        """Generate and attach request ID to the request."""
        request.id = str(uuid.uuid4())

        # Store in thread-local storage for logging
        from .logging_filters import request_id_context

        request_id_context.request_id = request.id

    def process_response(self, request, response):
        """Add request ID to response headers."""
        if hasattr(request, "id"):
            response["X-Request-ID"] = request.id

        # Clean up thread-local storage
        from .logging_filters import request_id_context

        request_id_context.request_id = None

        return response

    def process_exception(self, request, exception):
        """Ensure request ID is logged even when exceptions occur."""
        if hasattr(request, "id"):
            logger = logging.getLogger(__name__)
            logger.error(
                f"Exception in request {request.id}: {exception}",
                exc_info=True,
                extra={"request_id": request.id},
            )
