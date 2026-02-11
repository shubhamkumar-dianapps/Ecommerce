"""
Trigger Logs Script

This script makes HTTP requests to various endpoints to generate different types of logs.
Use this to verify that logging is working correctly across all log files.

Usage:
    python trigger_logs.py

Expected Logs:
    - general.log: All requests
    - api.log: API requests and errors (404, 401)
    - security.log: Failed login, password reset attempts
    - error.log: Warnings and errors (400, 404, 401)
"""

import requests

BASE_URL = "http://localhost:8000"


def test_logs():
    print("[*] Testing endpoints to generate logs...\n")

    # 1. INFO/API log - Health check
    try:
        resp = requests.get(f"{BASE_URL}/api/health/")
        print(f"[OK] Health Check: {resp.status_code}")
    except Exception as e:
        print(f"[FAIL] Health Check Failed: {e}")

    # 2. INFO/API log - Products list
    try:
        resp = requests.get(f"{BASE_URL}/api/v1/products/")
        print(f"[OK] Products List: {resp.status_code}")
        # Extract request ID from response header
        request_id = resp.headers.get("X-Request-ID", "N/A")
        print(f"   Request ID: {request_id}")
    except Exception as e:
        print(f"[FAIL] Products List Failed: {e}")

    # 3. SECURITY/ERROR log - Failed login
    try:
        data = {"email": "invalid@example.com", "password": "wrongpassword"}
        resp = requests.post(f"{BASE_URL}/api/v1/accounts/login/", json=data)
        print(f"[OK] Failed Login: {resp.status_code} (Expected 400)")
        request_id = resp.headers.get("X-Request-ID", "N/A")
        print(f"   Request ID: {request_id}")
    except Exception as e:
        print(f"[FAIL] Login Failed: {e}")

    # 4. ERROR/API log - Invalid route
    try:
        resp = requests.get(f"{BASE_URL}/invalid-route/")
        print(f"[OK] Invalid Route: {resp.status_code} (Expected 404)")
        request_id = resp.headers.get("X-Request-ID", "N/A")
        print(f"   Request ID: {request_id}")
    except Exception as e:
        print(f"[FAIL] Invalid Route Failed: {e}")

    # 5. AUTH error - Accessing cart without token
    try:
        resp = requests.get(f"{BASE_URL}/api/v1/cart/")
        print(f"[OK] Cart (No Auth): {resp.status_code} (Expected 401)")
        request_id = resp.headers.get("X-Request-ID", "N/A")
        print(f"   Request ID: {request_id}")
    except Exception as e:
        print(f"[FAIL] Cart Failed: {e}")

    # 6. SECURITY log - Password reset for non-existent user
    try:
        data = {"email": "notfound@example.com"}
        resp = requests.post(f"{BASE_URL}/api/v1/accounts/password-reset/", json=data)
        print(f"[OK] Password Reset (Not Found): {resp.status_code}")
        request_id = resp.headers.get("X-Request-ID", "N/A")
        print(f"   Request ID: {request_id}")
    except Exception as e:
        print(f"[FAIL] Password Reset Failed: {e}")

    print("\n" + "=" * 60)
    print("[INFO] Check the following log files:")
    print("   - logs/general.log   (all requests)")
    print("   - logs/api.log       (API requests, 404s, 401s)")
    print("   - logs/security.log  (failed login, password reset)")
    print("   - logs/error.log     (warnings and errors)")
    print("=" * 60)
    print("\n[TIP] Search logs by Request ID:")
    print("   grep '<request-id>' logs/*.log")


if __name__ == "__main__":
    test_logs()
