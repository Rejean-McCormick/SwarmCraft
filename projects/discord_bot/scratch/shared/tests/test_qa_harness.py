import os
import json
import random
import urllib.request
import urllib.error
from urllib.parse import urlencode

# Simple HTTP helpers using stdlib to avoid extra dependencies

def _post_json(url, payload, token=None):
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", "Accept": "application/json"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.getcode()
            body = resp.read()
            try:
                return status, json.loads(body.decode())
            except Exception:
                return status, None
    except urllib.error.HTTPError as e:
        body = e.read()
        try:
            payload = json.loads(body.decode())
        except Exception:
            payload = None
        return e.code, payload


def _get_json(url, token=None):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.getcode()
            body = resp.read()
            try:
                return status, json.loads(body.decode())
            except Exception:
                return status, None
    except urllib.error.HTTPError as e:
        body = e.read()
        try:
            payload = json.loads(body.decode())
        except Exception:
            payload = None
        return e.code, payload


# ENDPOINTS (assumed contract per project plan)
# POST /auth/register
# POST /auth/login
# GET /wallet/balance
# POST /shop/purchase
# GET /games/leaderboard


def _base_url():
    return os.environ.get("QA_BASE_URL", "http://localhost:8000")


def _random_email():
    return f"qa.user.{random.randint(100000,999999)}@example.test"


def test_end_to_end_auth_wallet_shop_games_flow():
    base = _base_url()
    # 1) Register
    email = _random_email()
    reg_url = f"{base}/auth/register"
    reg_payload = {"email": email, "password": "Secret123!"}
    status, reg_resp = _post_json(reg_url, reg_payload)
    assert status in (200, 201), f"Register failed: status={status}, body={reg_resp}"
    user_id = reg_resp.get("user_id") if reg_resp else None
    token = reg_resp.get("token") if reg_resp else None
    assert user_id is not None, f"Register did not return user_id: {reg_resp}"
    assert token is not None, f"Register did not return token: {reg_resp}"

    # 2) Login
    login_url = f"{base}/auth/login"
    login_payload = {"email": email, "password": "Secret123!"}
    status, login_resp = _post_json(login_url, login_payload)
    assert status == 200, f"Login failed: status={status}, body={login_resp}"
    login_token = login_resp.get("token") or login_resp.get("access_token")
    assert login_token, f"Login did not return token: {login_resp}"

    # 3) Wallet balance
    balance_url = f"{base}/wallet/balance"
    status, balance_resp = _get_json(balance_url, login_token)
    assert status == 200, f"Balance fetch failed: status={status}, body={balance_resp}"
    assert isinstance(balance_resp, dict) and "balance" in balance_resp, f"Invalid balance response: {balance_resp}"

    # 4) Shop purchase
    purchase_url = f"{base}/shop/purchase"
    purchase_payload = {"item_id": "item-xyz", "quantity": 1}
    status, purchase_resp = _post_json(purchase_url, purchase_payload, login_token)
    assert status == 200, f"Purchase failed: status={status}, body={purchase_resp}"
    assert isinstance(purchase_resp, dict) and (
        "purchase_id" in purchase_resp or "order_id" in purchase_resp
    ), f"Invalid purchase response: {purchase_resp}"

    # 5) Leaderboard / Games (read-only)
    leaderboard_url = f"{base}/games/leaderboard"
    status, lb_resp = _get_json(leaderboard_url, login_token)
    assert status == 200, f"Leaderboard fetch failed: status={status}, body={lb_resp}"
    assert isinstance(lb_resp, list)


def test_auth_and_security_failure_modes():
    base = _base_url()
    # Attempt to register with invalid email format
    reg_url = f"{base}/auth/register"
    status, resp = _post_json(reg_url, {"email": "not-an-email", "password": "Secret123!"})
    assert status in (400, 422), f"Invalid email should fail: status={status}, body={resp}"

    # Attempt login with wrong password (use previously created user if any fails will be fine)
    email = _random_email()
    # Create new user for predictable login failure
    reg_status, reg_resp = _post_json(reg_url, {"email": email, "password": "Secret123!"})
    if reg_status in (200, 201):
        # Try login with wrong password
        login_url = f"{base}/auth/login"
        login_status, login_resp = _post_json(login_url, {"email": email, "password": "WrongPass!"})
        assert login_status in (400, 401, 403), f"Wrong password should fail: status={login_status}, body={login_resp}"
    else:
        # If registration failed for some reason, we skip this subtest gracefully
        pass

    # Access wallet without token should fail
    balance_url = f"{base}/wallet/balance"
    status, resp = _get_json(balance_url, token=None)
    assert status in (401, 403), f"Unauthenticated balance fetch should fail: status={status}"

    # Purchase with invalid token should fail
    purchase_url = f"{base}/shop/purchase"
    status, resp = _post_json(purchase_url, {"item_id": "item-xyz", "quantity": 1}, token="invalid-token")
    assert status in (401, 403), f"Purchase with invalid token should fail: status={status}"

