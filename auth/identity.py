"""Google Identity Platform (Firebase Auth) integration — pure Python, no JS SDK."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

import requests

from config.settings import settings
from cloud.logging_config import get_logger

log = get_logger(__name__)

# ── Firebase Admin SDK (token verification) ────────────────────────────────────
_firebase_app = None


def _get_firebase_app():
    global _firebase_app
    if _firebase_app is None:
        try:
            import firebase_admin
            from firebase_admin import credentials

            cred_path = settings.FIREBASE_CREDENTIALS_PATH
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
            else:
                # On Cloud Run, use Application Default Credentials
                cred = credentials.ApplicationDefault()

            _firebase_app = firebase_admin.initialize_app(cred)
            log.info("Firebase Admin SDK initialised")
        except Exception as exc:
            log.error("Firebase Admin init failed: %s", exc)
    return _firebase_app


@dataclass
class AuthResult:
    success: bool
    uid: Optional[str] = None
    email: Optional[str] = None
    id_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    error: Optional[str] = None


# ── REST API helpers ───────────────────────────────────────────────────────────

def _firebase_post(url: str, payload: dict) -> tuple[bool, dict]:
    """POST to Firebase Auth REST API, returns (success, data)."""
    if not settings.FIREBASE_API_KEY:
        return False, {"error": {"message": "FIREBASE_API_KEY not configured"}}
    try:
        resp = requests.post(
            url,
            params={"key": settings.FIREBASE_API_KEY},
            json=payload,
            timeout=10,
        )
        data = resp.json()
        return resp.ok, data
    except requests.RequestException as exc:
        log.error("Firebase REST error: %s", exc)
        return False, {"error": {"message": str(exc)}}


def _parse_firebase_error(data: dict) -> str:
    msg = data.get("error", {}).get("message", "Authentication error")
    friendly = {
        "EMAIL_EXISTS": "An account with this email already exists.",
        "EMAIL_NOT_FOUND": "No account found with this email.",
        "INVALID_PASSWORD": "Incorrect password.",
        "INVALID_EMAIL": "Please enter a valid email address.",
        "WEAK_PASSWORD : Password should be at least 6 characters": "Password must be at least 6 characters.",
        "TOO_MANY_ATTEMPTS_TRY_LATER": "Too many attempts. Please try again later.",
        "USER_DISABLED": "This account has been disabled.",
        "INVALID_LOGIN_CREDENTIALS": "Invalid email or password.",
    }
    return friendly.get(msg, msg.replace("_", " ").capitalize())


# ── Public auth functions ──────────────────────────────────────────────────────

def sign_up(email: str, password: str) -> AuthResult:
    """Create a new user with email/password."""
    ok, data = _firebase_post(
        settings.FIREBASE_SIGN_UP_URL,
        {"email": email, "password": password, "returnSecureToken": True},
    )
    if ok:
        return AuthResult(
            success=True,
            uid=data["localId"],
            email=data["email"],
            id_token=data["idToken"],
            refresh_token=data["refreshToken"],
            expires_in=int(data.get("expiresIn", 3600)),
        )
    return AuthResult(success=False, error=_parse_firebase_error(data))


def sign_in(email: str, password: str) -> AuthResult:
    """Sign in with email/password."""
    ok, data = _firebase_post(
        settings.FIREBASE_SIGN_IN_URL,
        {"email": email, "password": password, "returnSecureToken": True},
    )
    if ok:
        return AuthResult(
            success=True,
            uid=data["localId"],
            email=data["email"],
            id_token=data["idToken"],
            refresh_token=data["refreshToken"],
            expires_in=int(data.get("expiresIn", 3600)),
        )
    return AuthResult(success=False, error=_parse_firebase_error(data))


def send_password_reset(email: str) -> AuthResult:
    """Send a password reset email."""
    ok, data = _firebase_post(
        settings.FIREBASE_RESET_URL,
        {"requestType": "PASSWORD_RESET", "email": email},
    )
    if ok:
        return AuthResult(success=True, email=data.get("email"))
    return AuthResult(success=False, error=_parse_firebase_error(data))


def refresh_id_token(refresh_token: str) -> AuthResult:
    """Exchange a refresh token for a new ID token."""
    ok, data = _firebase_post(
        settings.FIREBASE_REFRESH_URL,
        {"grant_type": "refresh_token", "refresh_token": refresh_token},
    )
    if ok:
        return AuthResult(
            success=True,
            uid=data.get("user_id"),
            id_token=data["id_token"],
            refresh_token=data["refresh_token"],
            expires_in=int(data.get("expires_in", 3600)),
        )
    return AuthResult(success=False, error=_parse_firebase_error(data))


def verify_id_token(id_token: str) -> Optional[dict]:
    """Verify a Firebase ID token using the Admin SDK. Returns decoded token or None."""
    try:
        _get_firebase_app()
        from firebase_admin import auth
        decoded = auth.verify_id_token(id_token)
        return decoded
    except Exception as exc:
        log.warning("Token verification failed: %s", exc)
        return None
