"""
Redis Cache Utility with Comprehensive Logging

This module provides a wrapper around Django's cache framework to log all
Redis operations including cache hits, misses, sets, and deletes.
"""

import logging
from typing import Any, Optional
from django.core.cache import cache

# Get logger for Redis operations
redis_logger = logging.getLogger("redis")


class CacheLogger:
    """
    Wrapper around Django cache with comprehensive logging.

    Usage:
        from apps.core.cache_utils import cache_logger

        # Get from cache
        value = cache_logger.get("my_key", default=None)

        # Set to cache
        cache_logger.set("my_key", value, timeout=300)
    """

    @staticmethod
    def get(key: str, default: Any = None, version: Optional[int] = None) -> Any:
        """
        Get value from cache with logging.

        Args:
            key: Cache key
            default: Default value if key not found
            version: Cache version

        Returns:
            Cached value or default
        """
        try:
            value = cache.get(key, default=default, version=version)

            if value is None or value == default:
                redis_logger.info(f"Cache MISS: {key}")
            else:
                redis_logger.info(f"Cache HIT: {key}")

            return value
        except Exception as e:
            redis_logger.error(f"Cache GET error for key '{key}': {e}", exc_info=True)
            return default

    @staticmethod
    def set(
        key: str,
        value: Any,
        timeout: Optional[int] = None,
        version: Optional[int] = None,
    ) -> bool:
        """
        Set value in cache with logging.

        Args:
            key: Cache key
            value: Value to cache
            timeout: Cache timeout in seconds
            version: Cache version

        Returns:
            True if successful, False otherwise
        """
        try:
            cache.set(key, value, timeout=timeout, version=version)
            redis_logger.info(
                f"Cache SET: {key} | Timeout: {timeout}s | Size: {len(str(value))} bytes"
            )
            return True
        except Exception as e:
            redis_logger.error(f"Cache SET error for key '{key}': {e}", exc_info=True)
            return False

    @staticmethod
    def delete(key: str, version: Optional[int] = None) -> bool:
        """
        Delete value from cache with logging.

        Args:
            key: Cache key
            version: Cache version

        Returns:
            True if successful, False otherwise
        """
        try:
            cache.delete(key, version=version)
            redis_logger.info(f"Cache DELETE: {key}")
            return True
        except Exception as e:
            redis_logger.error(
                f"Cache DELETE error for key '{key}': {e}", exc_info=True
            )
            return False

    @staticmethod
    def get_or_set(
        key: str,
        default: Any,
        timeout: Optional[int] = None,
        version: Optional[int] = None,
    ) -> Any:
        """
        Get value from cache, or set it if not found.

        Args:
            key: Cache key
            default: Callable or value to set if key not found
            timeout: Cache timeout in seconds
            version: Cache version

        Returns:
            Cached value or newly set value
        """
        try:
            value = cache.get(key, version=version)

            if value is None:
                redis_logger.info(f"Cache MISS (get_or_set): {key} | Setting new value")
                # If default is callable, call it
                if callable(default):
                    value = default()
                else:
                    value = default
                cache.set(key, value, timeout=timeout, version=version)
                redis_logger.info(
                    f"Cache SET (get_or_set): {key} | Timeout: {timeout}s"
                )
            else:
                redis_logger.info(f"Cache HIT (get_or_set): {key}")

            return value
        except Exception as e:
            redis_logger.error(
                f"Cache GET_OR_SET error for key '{key}': {e}", exc_info=True
            )
            # Fallback to computing the value
            if callable(default):
                return default()
            return default

    @staticmethod
    def invalidate_pattern(pattern: str) -> int:
        """
        Invalidate all cache keys matching a pattern.

        Args:
            pattern: Pattern to match (e.g., "product:*")

        Returns:
            Number of keys deleted
        """
        try:
            # Note: This requires django-redis backend
            from django_redis import get_redis_connection

            conn = get_redis_connection("default")
            keys = conn.keys(f"ecommerce:{pattern}")

            if keys:
                count = conn.delete(*keys)
                redis_logger.info(
                    f"Cache INVALIDATE pattern '{pattern}': {count} keys deleted"
                )
                return count
            else:
                redis_logger.info(
                    f"Cache INVALIDATE pattern '{pattern}': No keys found"
                )
                return 0
        except Exception as e:
            redis_logger.error(
                f"Cache INVALIDATE error for pattern '{pattern}': {e}", exc_info=True
            )
            return 0


# Singleton instance for easy import
cache_logger = CacheLogger()
