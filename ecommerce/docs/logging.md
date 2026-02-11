# Logging Guide

## Overview

This Django e-commerce application uses a comprehensive, production-grade logging system with:
- **Environment-based configuration** (console logs only in DEBUG mode)
- **Request ID tracking** (trace requests across log files)
- **Specialized log files** (security, payments, API, cache, tasks)
- **SQL logging toggle** (debug database queries)
- **Sentry integration** (optional error tracking)
- **Automatic log rotation** (prevents disk space issues)

---

## Log Files

All logs are stored in `logs/` directory:

| File | Purpose | Retention |
|------|---------|-----------|
| `general.log` | General application logs | 5 backups |
| `error.log` | Warnings and errors only | 10 backups |
| `security.log` | Authentication, authorization, audits | 30 backups |
| `database.log` | SQL queries (when enabled) | 3 backups |
| `api.log` | API requests, 404s, 500s | 5 backups |
| `payment.log` | Payment transactions | 50 backups |
| `redis.log` | Cache operations (hits/misses) | 10 backups |
| `celery.log` | Background task lifecycle | 10 backups |

---

## Request ID Tracking

Every request gets a unique UUID that appears in all logs:

```
INFO 2026-02-11 14:30:45 views 12345 67890 [a1b2c3d4-e5f6-7890-abcd-ef1234567890] User logged in
```

**Benefits:**
- Trace a single request across multiple log files
- Debug complex workflows
- Correlate errors with specific requests

**Response Header:**
```
X-Request-ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

---

## Environment Variables

### `.env` Configuration

```env
# Enable/disable console logging (development only)
DEBUG=True

# SQL query logging (set to True to log all queries)
LOG_SQL=False

# Environment name (appears in Sentry)
ENVIRONMENT=development

# Sentry error tracking (leave empty to disable)
SENTRY_DSN=
SENTRY_TRACES_SAMPLE_RATE=0.1
```

---

## Usage Examples

### 1. Basic Logging

```python
import logging

logger = logging.getLogger(__name__)

logger.info("User registered successfully")
logger.warning("Unusual activity detected")
logger.error("Payment processing failed", exc_info=True)
```

### 2. Security Logging

```python
from apps.accounts.services import AuditService

AuditService.log_login_attempt(
    user=user,
    ip_address=request.META.get('REMOTE_ADDR'),
    success=True
)
```

### 3. Redis Cache Logging

```python
from apps.core.cache_utils import cache_logger

# Automatically logs HIT/MISS/SET
data = cache_logger.get("product:123")
cache_logger.set("product:123", data, timeout=3600)
```

### 4. Celery Task Logging

```python
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_order(order_id):
    logger.info(f"Processing order {order_id}")
    # Task lifecycle is automatically logged
```

---

## Debugging

### Enable SQL Logging

```bash
# In .env
LOG_SQL=True

# Restart server
python manage.py runserver
```

Check `logs/database.log` for all SQL queries.

### Monitor Logs in Real-Time

**PowerShell:**
```powershell
Get-Content logs\general.log -Wait
Get-Content logs\celery.log -Wait
```

**Linux/Mac:**
```bash
tail -f logs/general.log
tail -f logs/celery.log
```

### Search Logs by Request ID

```bash
# Find all logs for a specific request
grep "a1b2c3d4-e5f6-7890-abcd-ef1234567890" logs/*.log
```

---

## Production Deployment

### 1. Environment Configuration

```env
# Production .env
DEBUG=False
LOG_SQL=False
ENVIRONMENT=production
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

### 2. Log Rotation Setup

```bash
# Copy logrotate config
sudo cp deployment/logrotate.conf /etc/logrotate.d/ecommerce

# Edit paths
sudo nano /etc/logrotate.d/ecommerce

# Test configuration
sudo logrotate -d /etc/logrotate.d/ecommerce

# Force rotation (testing)
sudo logrotate -f /etc/logrotate.d/ecommerce
```

### 3. Monitor Disk Usage

```bash
# Check log directory size
du -sh logs/

# Find large log files
find logs/ -type f -size +10M
```

---

## Sentry Integration

### Setup

1. **Install Sentry SDK:**
   ```bash
   pip install sentry-sdk
   ```

2. **Configure `.env`:**
   ```env
   SENTRY_DSN=https://your-key@sentry.io/project-id
   SENTRY_TRACES_SAMPLE_RATE=0.1  # 10% of transactions
   ENVIRONMENT=production
   ```

3. **Restart application**

### Features

- **Automatic error capture** (exceptions, 500 errors)
- **Performance monitoring** (slow queries, API calls)
- **Release tracking** (correlate errors with deployments)
- **Privacy-first** (`send_default_pii=False`)
- **DEBUG mode ignored** (no errors sent in development)

### Test Sentry

```python
# In Django shell
python manage.py shell

>>> raise Exception("Test Sentry integration")
```

Check your Sentry dashboard for the error.

---

## Best Practices

### 1. Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Something unexpected but not an error
- **ERROR**: Serious problem, needs attention
- **CRITICAL**: System failure, immediate action required

### 2. Structured Logging

```python
# Good: Structured data
logger.info("Order created", extra={
    'order_id': order.id,
    'user_id': user.id,
    'total': order.total
})

# Avoid: Unstructured strings
logger.info(f"Order {order.id} created by {user.id}")
```

### 3. Security

- **Never log passwords or tokens**
- **Sanitize sensitive data** (credit cards, SSNs)
- **Use security logger** for authentication events

### 4. Performance

- **Avoid excessive logging** in hot paths
- **Use appropriate log levels** (DEBUG only when needed)
- **Monitor log file sizes** regularly

---

## Troubleshooting

### Logs not appearing?

1. Check `DEBUG` setting in `.env`
2. Verify `logs/` directory exists and is writable
3. Check file permissions: `chmod 755 logs/`

### Request IDs showing as `-`?

- Middleware not installed or disabled
- Check `MIDDLEWARE` in `config/settings/base.py`

### Sentry not capturing errors?

1. Verify `SENTRY_DSN` is set
2. Check `DEBUG=False` (Sentry ignores DEBUG mode)
3. Test with: `raise Exception("Test")`

---

## Advanced Configuration

### Custom Logger

```python
# In your app
import logging

logger = logging.getLogger('apps.myapp')
logger.info("Custom app log")
```

### Add to `logging.py`:

```python
"loggers": {
    "apps.myapp": {
        "handlers": ["file_general"],
        "level": "INFO",
        "propagate": False,
    },
}
```

---

## Monitoring Checklist

- [ ] Log files rotating correctly
- [ ] Disk space usage under control
- [ ] Sentry receiving errors (if configured)
- [ ] Request IDs appearing in logs
- [ ] SQL logging disabled in production
- [ ] Console logging disabled in production
- [ ] Security logs capturing auth events
- [ ] Payment logs recording transactions
