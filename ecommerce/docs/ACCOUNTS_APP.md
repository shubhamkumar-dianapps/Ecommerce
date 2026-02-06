# Accounts App - Complete Technical Documentation

> **Last Updated**: February 2026  
> **Author**: AI Pair Programmer  
> **Purpose**: This document explains the **thought process**, **why**, **what**, and **how** behind every component of the accounts app.

---

## Table of Contents

1. [Philosophy & Design Decisions](#1-philosophy--design-decisions)
2. [Directory Structure](#2-directory-structure)
3. [Models Deep Dive](#3-models-deep-dive)
4. [Authentication Flows](#4-authentication-flows)
5. [Audit Logging System](#5-audit-logging-system)
6. [File-Based Logging](#6-file-based-logging)
7. [Services Layer](#7-services-layer)
8. [Permissions & Security](#8-permissions--security)
9. [API Endpoints](#9-api-endpoints)
10. [Common Questions](#10-common-questions)

---

## 1. Philosophy & Design Decisions

### 1.1 Why a Custom User Model?

**The Problem**: Django's default `User` model uses `username` as the primary identifier. In modern e-commerce, email is the standard.

**Our Solution**: We created a custom `User` model with:
- `email` as the login identifier (not username)
- `role` field for Customer vs. Shopkeeper distinction
- `is_deleted` for soft deletes (never lose transaction history)

**Why This Matters**: If a user deletes their account, we can't delete their past orders (legal/accounting reasons). Soft delete keeps the data but hides the user.

---

### 1.2 Why Token-Based Flows?

**The Problem**: How do you verify that someone clicking a "Reset Password" link is actually the account owner?

**The Thought Process**:
1. User requests password reset → We generate a **random UUID token**
2. We email that token as a link → Only the email owner sees it
3. User clicks link → They provide the token back to us
4. We verify token → Grant access

**Why UUID?**: A UUID4 has 3.4×10³⁸ possible combinations. A hacker randomly guessing a valid token is statistically impossible.

---

### 1.3 Why Audit Logging?

**The Problem**: Six months from now, a user complains: "Someone changed my email without my permission!"

**Without Audit Logs**: You have no evidence of what happened.

**With Audit Logs**: You can immediately query:
```python
AuditLog.objects.filter(user=user, action="EMAIL_CHANGE_COMPLETE")
# Returns: {"from": "old@email.com", "to": "new@email.com", "created_at": "2026-01-15"}
```

**The Design Decision**: We store security events in **two places**:
1. **Database** (`AuditLog` model) → For querying and dashboards
2. **Log Files** (`security.log`) → For compliance and external monitoring tools

---

### 1.4 Why Compact Token Models?

**The Old Design** (Before Refactoring):
```python
class PasswordResetToken:
    user = ForeignKey(User)
    token = UUIDField()
    ip_address = GenericIPAddressField()  # Redundant
    user_agent = TextField()              # Redundant
```

**The Problem**: We were storing IP/UserAgent in **both** the token model **and** the AuditLog. This is data duplication.

**The New Design**:
```python
class PasswordResetToken:
    user = ForeignKey(User)
    token = UUIDField()
    expires_at = DateTimeField()
    is_used = BooleanField()
    # That's it! IP/Agent is in AuditLog only.
```

**Why This Is Better**:
- Single source of truth
- Smaller database tables
- Easier maintenance

---

## 2. Directory Structure

```
apps/accounts/
├── models/
│   ├── __init__.py           # Exports all models
│   ├── user.py               # Custom User model
│   ├── profile.py            # CustomerProfile / ShopkeeperProfile
│   ├── user_session.py       # Active session tracking
│   ├── audit_log.py          # Security event logging
│   ├── email_verification_token.py
│   ├── password_reset_token.py
│   └── email_change_token.py
│
├── services/
│   ├── auth_service.py       # JWT & session management
│   ├── email_service.py      # Email sending logic
│   ├── audit_service.py      # Audit log creation
│   └── password_reset_service.py  # Password reset & email change
│
├── serializers/
│   ├── user.py               # User CRUD serializers
│   ├── auth.py               # Login/Register serializers
│   └── password_reset.py     # Password reset serializers
│
├── views/
│   ├── auth.py               # Login/Logout/Register views
│   ├── user.py               # Profile management views
│   └── password_reset.py     # Password reset views
│
├── permissions/
│   └── base.py               # IsEmailVerified, IsActiveUser, etc.
│
├── v1/
│   └── urls.py               # API URL routing
│
├── constants.py              # All magic strings/numbers
├── validators.py             # Phone, GST, Password validators
└── utils.py                  # Helper functions (get_client_ip, etc.)
```

---

## 3. Models Deep Dive

### 3.1 User Model

**Location**: `models/user.py`

```python
class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        CUSTOMER = "CUSTOMER", "Customer"
        SHOPKEEPER = "SHOPKEEPER", "Shopkeeper"
        ADMIN = "ADMIN", "Admin"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    email = models.EmailField(unique=True)
    phone = PhoneNumberField(blank=True, null=True)
    role = models.CharField(max_length=20, choices=Role.choices)
    email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)  # Soft delete
    
    USERNAME_FIELD = "email"  # Login with email, not username
```

**Why UUID for Primary Key?**
- Prevents ID enumeration attacks (hacker can't guess `/users/1`, `/users/2`)
- Safe to expose in URLs
- Globally unique across all tables

**Why Soft Delete?**
- User deletes account → `is_deleted = True`
- Old orders still reference this user (foreign key intact)
- Compliant with data retention laws

---

### 3.2 AuditLog Model

**Location**: `models/audit_log.py`

```python
class AuditLog(models.Model):
    class Action(models.TextChoices):
        LOGIN = "LOGIN"
        LOGOUT = "LOGOUT"
        FAILED_LOGIN = "FAILED_LOGIN"
        PASSWORD_CHANGE = "PASSWORD_CHANGE"
        PASSWORD_RESET_REQUEST = "PASSWORD_RESET_REQUEST"
        PASSWORD_RESET_COMPLETE = "PASSWORD_RESET_COMPLETE"
        EMAIL_VERIFICATION = "EMAIL_VERIFICATION"
        EMAIL_CHANGE_REQUEST = "EMAIL_CHANGE_REQUEST"
        EMAIL_CHANGE_COMPLETE = "EMAIL_CHANGE_COMPLETE"  # ← Stores email history!
        ACCOUNT_CREATED = "ACCOUNT_CREATED"
        ACCOUNT_DEACTIVATED = "ACCOUNT_DEACTIVATED"
        ACCOUNT_REACTIVATED = "ACCOUNT_REACTIVATED"
        SESSION_REVOKED = "SESSION_REVOKED"
        # ... more actions

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50, choices=Action.choices)
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)  # ← Flexible storage!
    created_at = models.DateTimeField(auto_now_add=True)
```

**Why `metadata` is a JSONField?**
Each action needs different data:
- `FAILED_LOGIN`: `{"email": "test@test.com", "reason": "Invalid password"}`
- `EMAIL_CHANGE_COMPLETE`: `{"from": "old@test.com", "to": "new@test.com"}`
- `PASSWORD_RESET_REQUEST`: `{}` (no extra data needed)

JSONField gives us flexibility without creating separate tables for each action type.

---

### 3.3 PasswordResetToken Model (Compact Design)

**Location**: `models/password_reset_token.py`

```python
class PasswordResetToken(models.Model):
    EXPIRY_HOURS = 1  # Short lifetime = more secure

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    # NOTE: IP/UserAgent removed - stored in AuditLog instead

    def is_valid(self) -> bool:
        return not self.is_used and timezone.now() < self.expires_at
```

**Why 1-Hour Expiry?**
Password reset is high-risk. If a hacker gets the email, they have limited time to act. Email verification uses 24 hours because it's lower risk (account not yet active).

---

### 3.4 EmailChangeToken Model

**Location**: `models/email_change_token.py`

```python
class EmailChangeToken(models.Model):
    EXPIRY_HOURS = 24

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    current_email = models.EmailField()  # ← Snapshot at request time
    new_email = models.EmailField()
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def is_valid(self) -> bool:
        return (
            not self.is_used
            and timezone.now() < self.expires_at
            and self.user.email == self.current_email  # ← Security check!
        )
```

**Why Store `current_email`?**

**Scenario Without It**:
1. User has email `alice@test.com`
2. User requests change to `bob@test.com` → Token created
3. Before clicking link, user somehow changes email to `charlie@test.com`
4. User clicks the old link → Email becomes `bob@test.com`
5. **Problem**: User expected `charlie@test.com` but got `bob@test.com`!

**With `current_email` Snapshot**:
- Step 4 fails because `user.email != token.current_email`
- Token is invalidated automatically

---

## 4. Authentication Flows

### 4.1 Registration Flow (Atomic)

```
┌─────────────────────────────────────────────────────────────────┐
│                      REGISTRATION FLOW                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. User submits: email, password, phone, role                  │
│              ↓                                                  │
│  2. Validate: unique email, password strength, phone format     │
│              ↓                                                  │
│  3. START TRANSACTION (@transaction.atomic)                     │
│              ↓                                                  │
│  4. Create User with email_verified=False                       │
│              ↓                                                  │
│  5. Create Profile (CustomerProfile or ShopkeeperProfile)       │
│              ↓                                                  │
│  6. Schedule Email (transaction.on_commit)                      │
│              ↓                                                  │
│  7. Log ACCOUNT_CREATED in AuditLog                             │
│              ↓                                                  │
│  8. COMMIT TRANSACTION                                          │
│              ↓                                                  │
│  9. SEND EMAIL (Only after commit success)                      │
│              ↓                                                  │
│  10. Return JWT tokens + Standardized Response                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Atomicity Guarantee**: If the database crashes or the audit log fails during steps 4-7, the entire transaction rolls back. No user is created, and no email is sent. This prevents "ghost" unverified accounts.

**Why `on_commit`?**: We only send the email after the database has successfully saved the user. This prevents a race condition where a background email worker tries to find a user that hasn't been committed yet.

---

### 4.2 Password Reset Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    PASSWORD RESET FLOW                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  STEP 1: REQUEST                                                │
│  ─────────────────                                              │
│  User submits: email                                            │
│              ↓                                                  │
│  Check if user exists                                           │
│              ↓                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ SECURITY: Always return "Email sent" even if user       │    │
│  │ doesn't exist. Prevents email enumeration attacks.      │    │
│  └─────────────────────────────────────────────────────────┘    │
│              ↓                                                  │
│  If user exists:                                                │
│    - Delete any old unused tokens (prevent token hoarding)      │
│    - Create new PasswordResetToken (1h expiry)                  │
│    - Log PASSWORD_RESET_REQUEST in AuditLog                     │
│    - Send email with reset link                                 │
│                                                                 │
│  STEP 2: CONFIRM                                                │
│  ───────────────                                                │
│  User submits: token, new_password, confirm_password            │
│              ↓                                                  │
│  Validate token (exists, not used, not expired)                 │
│              ↓                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ SECURITY: Use select_for_update() to lock both Token    │    │
│  │ and User rows. Prevents race conditions and             │    │
│  │ double-submissions.                                     │    │
│  └─────────────────────────────────────────────────────────┘    │
│              ↓                                                  │
│  Update password using set_password() (auto-hashes)             │
│              ↓                                                  │
│  Mark token as used                                             │
│              ↓                                                  │
│  Log PASSWORD_RESET_COMPLETE in AuditLog                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### 4.3 Email Change Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     EMAIL CHANGE FLOW                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  STEP 1: REQUEST (Authenticated)                                │
│  ──────────────────────────────                                 │
│  User submits: current_password, new_email                      │
│              ↓                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ SECURITY: Require current password to prove identity.   │    │
│  │ If hacker has session cookie, they still can't change   │    │
│  │ email without knowing the password.                     │    │
│  └─────────────────────────────────────────────────────────┘    │
│              ↓                                                  │
│  Check new_email is not already in use                          │
│              ↓                                                  │
│  Create EmailChangeToken with:                                  │
│    - current_email = user's current email (snapshot)            │
│    - new_email = requested new email                            │
│              ↓                                                  │
│  Log EMAIL_CHANGE_REQUEST in AuditLog                           │
│              ↓                                                  │
│  Send verification email to NEW email address                   │
│  (Not the old one - this proves user controls new inbox)        │
│                                                                 │
│  STEP 2: CONFIRM                                                │
│  ───────────────                                                │
│  User clicks link from NEW inbox, sends: token                  │
│              ↓                                                  │
│  Validate token (exists, not used, not expired)                 │
│              ↓                                                  │
│  Check user.email == token.current_email (email unchanged)      │
│              ↓                                                  │
│  Check new_email still available (not taken since request)      │
│              ↓                                                  │
│  Update user.email = new_email                                  │
│              ↓                                                  │
│  Mark token as used                                             │
│              ↓                                                  │
│  Log EMAIL_CHANGE_COMPLETE in AuditLog:                         │
│    metadata = {"from": "old@test.com", "to": "new@test.com"}    │
│  ↑                                                              │
│  THIS IS THE PERMANENT HISTORY - Never deleted!                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Audit Logging System

### 5.1 AuditService

**Location**: `services/audit_service.py`

The AuditService is the central place for all security logging:

```python
class AuditService:
    @staticmethod
    def log_login(user, request):
        # Logs: LOGIN action with IP and UserAgent

    @staticmethod
    def log_failed_login(email, request, reason=None):
        # Logs: FAILED_LOGIN with email attempted

    @staticmethod
    def log_email_change_complete(user, old_email, new_email):
        # Logs: EMAIL_CHANGE_COMPLETE with {"from": ..., "to": ...}
        # ↑ THIS IS HOW WE KEEP EMAIL HISTORY!

    @staticmethod
    def log_password_reset_request(user, ip_address, user_agent):
        # Logs: PASSWORD_RESET_REQUEST

    # ... more methods for each action type
```

### 5.2 How to Query Email History

```python
from apps.accounts.models import AuditLog

# Get all email changes for a user
def get_email_history(user_id):
    return AuditLog.objects.filter(
        user_id=user_id,
        action="EMAIL_CHANGE_COMPLETE"
    ).order_by("-created_at").values("metadata", "created_at")

# Result:
# [
#     {"metadata": {"from": "v2@test.com", "to": "v3@test.com"}, "created_at": "2026-02-01"},
#     {"metadata": {"from": "v1@test.com", "to": "v2@test.com"}, "created_at": "2026-01-15"},
# ]
```

### 5.3 How to Detect Suspicious Activity

```python
# Find all failed logins from a specific IP in the last hour
from django.utils import timezone
from datetime import timedelta

suspicious_ip = "192.168.1.100"
one_hour_ago = timezone.now() - timedelta(hours=1)

failed_attempts = AuditLog.objects.filter(
    action="FAILED_LOGIN",
    ip_address=suspicious_ip,
    created_at__gte=one_hour_ago
).count()

if failed_attempts > 10:
    # Block this IP or require CAPTCHA
    pass
```

---

## 6. File-Based Logging

### 6.1 Log File Structure

**Location**: `config/settings/logging.py`

We create **6 separate log files**, each for a different purpose:

| File | Purpose | Rotation |
|------|---------|----------|
| `logs/general.log` | Application-wide INFO logs | 10MB, 5 backups |
| `logs/error.log` | Warnings and errors only | 10MB, 10 backups |
| `logs/security.log` | All security events (logins, password changes) | 10MB, **30 backups** |
| `logs/database.log` | SQL queries (DEBUG level) | 10MB, 3 backups |
| `logs/api.log` | API request logs | 10MB, 5 backups |
| `logs/payment.log` | Order/payment transactions | 10MB, **50 backups** |

**Why Different Retention?**
- Security and payment logs are kept longer (legal compliance)
- Database logs are mostly for debugging (shorter retention)

### 6.2 How Logs Are Written

Every time `AuditService._log_event()` is called, it **automatically** writes to both:

1. **Database**: `AuditLog.objects.create(...)`
2. **File**: `security_logger.info(f"AUDIT: {action} | User: {email} | ...")`

```python
# In audit_service.py
import logging
security_logger = logging.getLogger("security")

class AuditService:
    @staticmethod
    def _log_event(action, user, ip_address, user_agent, metadata):
        # Log to file
        user_email = user.email if user else "anonymous"
        security_logger.info(
            f"AUDIT: {action} | User: {user_email} | IP: {ip_address} | Metadata: {metadata}"
        )
        
        # Log to database
        return AuditLog.objects.create(...)
```

### 6.3 Sample Log Output

```
# logs/security.log
[2026-02-04 11:00:00] INFO | security | AUDIT: LOGIN | User: john@test.com | IP: 192.168.1.1 | Metadata: {}
[2026-02-04 11:05:00] INFO | security | AUDIT: PASSWORD_RESET_REQUEST | User: jane@test.com | IP: 10.0.0.5 | Metadata: {}
[2026-02-04 11:06:00] INFO | security | AUDIT: PASSWORD_RESET_COMPLETE | User: jane@test.com | IP: None | Metadata: {}
[2026-02-04 11:10:00] WARNING | security | Password reset attempted for non-existent email: fake@test.com | IP: 1.2.3.4
```

---

## 7. Services Layer

### 7.1 Why Use Services?

**Without Services** (Bad Pattern):
```python
# In views.py - Business logic mixed with HTTP handling
class PasswordResetView(APIView):
    def post(self, request):
        email = request.data["email"]
        user = User.objects.get(email=email)
        token = PasswordResetToken.objects.create(user=user)
        send_mail(...)  # Business logic in view!
```

**With Services** (Good Pattern):
```python
# In views.py - Clean and simple
class PasswordResetView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        success, message = PasswordResetService.request_password_reset(
            email=serializer.validated_data["email"],
            ip_address=get_client_ip(request),
        )
        return Response({"message": message})

# In services/password_reset_service.py - All logic here
class PasswordResetService:
    @staticmethod
    def request_password_reset(email, ip_address):
        # All business logic in one place
        # Easy to test, reuse, and maintain
```

### 7.2 Service Files

| Service | Responsibility |
|---------|---------------|
| `auth_service.py` | JWT generation, session management, login/logout |
| `email_service.py` | Email sending (verification, welcome, etc.) |
| `audit_service.py` | All audit log creation |
| `password_reset_service.py` | Password reset + email change flows |

---

## 8. Permissions & Security

### 8.1 Custom Permissions

**Location**: `permissions/base.py`

```python
class IsEmailVerified(BasePermission):
    """Require verified email for sensitive actions."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.email_verified

class IsActiveUser(BasePermission):
    """Block deleted users."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_active
```

### 8.2 Usage in Views

```python
class CheckoutView(APIView):
    permission_classes = [IsAuthenticated, IsEmailVerified]
    # ↑ User must be logged in AND have verified email

class ProfileView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]
    # ↑ User must be logged in AND not soft-deleted
```

### 8.3 Rate Limiting

Configured in `settings/base.py`:

```python
REST_FRAMEWORK = {
    "DEFAULT_THROTTLE_RATES": {
        "anon": "10/minute",    # Anonymous users
        "user": "1000/hour",    # Authenticated users
        "auth": "5/minute",     # Login/register endpoints
    },
}
```

---

## 9. API Endpoints

### 9.1 Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/accounts/register/` | Register new user | ❌ |
| POST | `/api/v1/accounts/login/` | Get JWT tokens | ❌ |
| POST | `/api/v1/accounts/logout/` | Invalidate session | ✅ |
| POST | `/api/v1/accounts/token/refresh/` | Refresh access token | ❌ (needs refresh token) |

### 9.2 Password & Email Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/accounts/password-reset/` | Request reset email | ❌ |
| POST | `/api/v1/accounts/password-reset/confirm/` | Set new password | ❌ (needs token) |
| POST | `/api/v1/accounts/email-change/` | Request email change | ✅ |
| POST | `/api/v1/accounts/email-change/confirm/` | Confirm new email | ❌ (needs token) |
| POST | `/api/v1/accounts/verify-email/` | Verify email address | ❌ (needs token) |

### 9.3 Profile Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/accounts/profile/` | Get current user profile | ✅ |
| PATCH | `/api/v1/accounts/profile/` | Update profile | ✅ |
| POST | `/api/v1/accounts/password-change/` | Change password | ✅ |

---

## 10. Common Questions

### Q1: How do I find a user's previous email addresses?

```python
from apps.accounts.models import AuditLog

AuditLog.objects.filter(
    user_id="<user-uuid>",
    action="EMAIL_CHANGE_COMPLETE"
).values_list("metadata__from", flat=True)
```

### Q2: How do I detect if a password reset was requested from a different IP than where it was completed?

```python
# Get the request log
request_log = AuditLog.objects.get(
    user=user,
    action="PASSWORD_RESET_REQUEST",
    created_at__gte=some_time
)

# Get the completion log
complete_log = AuditLog.objects.get(
    user=user,
    action="PASSWORD_RESET_COMPLETE",
    created_at__gte=request_log.created_at
)

if request_log.ip_address != complete_log.ip_address:
    # Suspicious! Different IPs
    pass
```

### Q3: Why is email verification 24 hours but password reset is 1 hour?

**Risk Level**:
- Email verification: Low risk (account not yet active)
- Password reset: High risk (grants full account access)

Higher risk = shorter expiry.

### Q4: What happens if two people click the same reset link simultaneously?

We use `select_for_update()` on both the **Token** and the **User** rows within an atomic transaction. This creates a database lock:
1. The first request locks the rows and succeeds.
2. The second request is forced to wait until the first one finishes.
3. Once the first finishes, the second request sees that `token.is_used = True` and fails gracefully.

This prevents any millisecond-level race conditions.

### Q5: Where do I configure log rotation?

In `config/settings/logging.py`:

```python
"file_security": {
    "class": "logging.handlers.RotatingFileHandler",
    "maxBytes": 10 * 1024 * 1024,  # 10 MB per file
    "backupCount": 30,             # Keep 30 old files
}
```

---

## Summary

This accounts app implements **production-grade authentication** with:

✅ Custom User model with role-based access  
✅ Token-based verification flows (email, password reset, email change)  
✅ Comprehensive audit logging (database + file)  
✅ Compact models (no redundant data)  
✅ Service layer for clean architecture  
✅ Rate limiting for security  

Every design decision was made with **security**, **maintainability**, and **compliance** in mind.
