"""
Test views for Redis and Celery logging verification.
"""

import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.core.cache_utils import cache_logger
from apps.accounts.tasks import send_verification_email_task

logger = logging.getLogger(__name__)


class TestLoggingView(APIView):
    """
    Test endpoint to verify Redis and Celery logging.

    GET /api/v1/test-logging/
    """

    permission_classes = []  # Allow anonymous access for testing

    def get(self, request):
        """Test all logging scenarios."""
        results = {}

        # ===================================================================
        # TEST 1: Cache MISS (first access)
        # ===================================================================
        test_key = "test:logging:demo"
        value = cache_logger.get(test_key)
        results["test_1_cache_miss"] = {
            "description": "First cache access (should be MISS)",
            "value": value,
            "check_log": "logs/redis.log for 'Cache MISS: test:logging:demo'",
        }

        # ===================================================================
        # TEST 2: Cache SET
        # ===================================================================
        test_data = {"message": "Hello from cache!", "timestamp": "2026-02-06"}
        cache_logger.set(test_key, test_data, timeout=60)
        results["test_2_cache_set"] = {
            "description": "Setting cache value",
            "data": test_data,
            "check_log": "logs/redis.log for 'Cache SET: test:logging:demo'",
        }

        # ===================================================================
        # TEST 3: Cache HIT (second access)
        # ===================================================================
        cached_value = cache_logger.get(test_key)
        results["test_3_cache_hit"] = {
            "description": "Second cache access (should be HIT)",
            "value": cached_value,
            "check_log": "logs/redis.log for 'Cache HIT: test:logging:demo'",
        }

        # ===================================================================
        # TEST 4: Cache GET_OR_SET (with existing value)
        # ===================================================================
        value_from_get_or_set = cache_logger.get_or_set(
            test_key, default={"fallback": "This won't be used"}, timeout=60
        )
        results["test_4_get_or_set_hit"] = {
            "description": "get_or_set with existing cache (should HIT)",
            "value": value_from_get_or_set,
            "check_log": "logs/redis.log for 'Cache HIT (get_or_set)'",
        }

        # ===================================================================
        # TEST 5: Cache GET_OR_SET (with new key)
        # ===================================================================
        new_key = "test:logging:new_key"
        new_value = cache_logger.get_or_set(
            new_key,
            default=lambda: {"computed": "This is a computed value"},
            timeout=60,
        )
        results["test_5_get_or_set_miss"] = {
            "description": "get_or_set with new key (should MISS then SET)",
            "value": new_value,
            "check_log": "logs/redis.log for 'Cache MISS (get_or_set)' and 'Cache SET (get_or_set)'",
        }

        # ===================================================================
        # TEST 6: Cache DELETE
        # ===================================================================
        cache_logger.delete(test_key)
        results["test_6_cache_delete"] = {
            "description": "Deleting cache key",
            "check_log": "logs/redis.log for 'Cache DELETE: test:logging:demo'",
        }

        # ===================================================================
        # TEST 7: Cache INVALIDATE pattern
        # ===================================================================
        # Set multiple keys with pattern
        cache_logger.set("test:pattern:1", "value1", timeout=60)
        cache_logger.set("test:pattern:2", "value2", timeout=60)
        cache_logger.set("test:pattern:3", "value3", timeout=60)

        # Invalidate all matching keys
        deleted_count = cache_logger.invalidate_pattern("test:pattern:*")
        results["test_7_invalidate_pattern"] = {
            "description": "Invalidating all keys matching pattern",
            "deleted_count": deleted_count,
            "check_log": "logs/redis.log for 'Cache INVALIDATE pattern'",
        }

        # ===================================================================
        # TEST 8: Trigger Celery Task (async)
        # ===================================================================
        # Note: This will fail if user doesn't exist, but will still log
        task_result = send_verification_email_task.delay(user_id=999)
        results["test_8_celery_task"] = {
            "description": "Triggering async Celery task",
            "task_id": str(task_result.id),
            "check_log": "logs/celery.log for task lifecycle events",
            "note": "Task will fail (user 999 doesn't exist) but will demonstrate retry logging",
        }

        # ===================================================================
        # TEST 9: Database fallback simulation
        # ===================================================================
        db_cache_key = "test:db_fallback"

        # Simulate cache miss -> DB query -> cache set
        cached_data = cache_logger.get(db_cache_key)
        if cached_data is None:
            # Simulate DB query
            logger.info("Simulating database query for missing cache")
            db_data = {"from": "database", "products": ["Product A", "Product B"]}
            cache_logger.set(db_cache_key, db_data, timeout=300)
            cached_data = db_data

        results["test_9_db_fallback"] = {
            "description": "Database fallback pattern (cache miss -> DB -> cache set)",
            "data": cached_data,
            "check_log": "logs/redis.log for MISS then SET sequence",
        }

        return Response(
            {
                "status": "success",
                "message": "Logging tests completed! Check the log files.",
                "instructions": {
                    "redis_logs": "tail -f logs/redis.log",
                    "celery_logs": "tail -f logs/celery.log",
                    "windows_redis": "Get-Content logs\\redis.log -Wait",
                    "windows_celery": "Get-Content logs\\celery.log -Wait",
                },
                "results": results,
            },
            status=status.HTTP_200_OK,
        )
