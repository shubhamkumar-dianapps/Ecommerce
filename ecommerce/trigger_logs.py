import requests

BASE_URL = "http://localhost:8001"


def test_logs():
    print("Testing endpoints to generate logs...")

    # 1. INFO/API log - Health check
    try:
        resp = requests.get(f"{BASE_URL}/api/health/")
        print(f"Health Check: {resp.status_code}")
    except Exception as e:
        print(f"Health Check Failed: {e}")

    # 2. INFO/API log - Products list
    try:
        resp = requests.get(f"{BASE_URL}/api/v1/products/")
        print(f"Products List: {resp.status_code}")
    except Exception as e:
        print(f"Products List Failed: {e}")

    # 3. SECURITY/ERROR log - Failed login
    try:
        data = {"email": "invalid@example.com", "password": "wrongpassword"}
        resp = requests.post(f"{BASE_URL}/api/v1/accounts/login/", json=data)
        print(f"Failed Login: {resp.status_code}")
    except Exception as e:
        print(f"Login Failed: {e}")

    # 4. ERROR/API log - Invalid route
    try:
        resp = requests.get(f"{BASE_URL}/invalid-route/")
        print(f"Invalid Route: {resp.status_code}")
    except Exception as e:
        print(f"Invalid Route Failed: {e}")

    # 5. AUTH error - Accessing cart without token
    try:
        resp = requests.get(f"{BASE_URL}/api/v1/cart/")
        print(f"Cart (No Auth): {resp.status_code}")
    except Exception as e:
        print(f"Cart Failed: {e}")

    # 6. SECURITY log - Password reset for non-existent user
    try:
        data = {"email": "notfound@example.com"}
        resp = requests.post(f"{BASE_URL}/api/v1/accounts/password-reset/", json=data)
        print(f"Password Reset (Not Found): {resp.status_code}")
    except Exception as e:
        print(f"Password Reset Failed: {e}")


if __name__ == "__main__":
    test_logs()
