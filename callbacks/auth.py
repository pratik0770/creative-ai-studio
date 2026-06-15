"""Authentication callbacks — login, signup, password reset."""

from datetime import datetime

from dash import Input, Output, State, callback, no_update
from flask import session as flask_session

import dash_bootstrap_components as dbc
from dash import html

from auth.identity import sign_in, sign_up, send_password_reset
from database.connection import get_session
from database.models import User
from config.settings import settings
from cloud.logging_config import get_logger

log = get_logger(__name__)

DEV_UID_PREFIX = "dev-local-"


def _upsert_user(uid: str, email: str) -> None:
    db = get_session()
    try:
        user = db.query(User).filter(User.id == uid).first()
        if user:
            user.last_login = datetime.utcnow()
        else:
            user = User(id=uid, email=email, last_login=datetime.utcnow())
            db.add(user)
        db.commit()
    except Exception as exc:
        db.rollback()
        log.error("upsert_user error: %s", exc)
    finally:
        db.close()


def register_auth_callbacks(app):

    # ── Login ──────────────────────────────────────────────────────────────────
    @app.callback(
        Output("login-alert", "children"),
        Output("login-alert", "color"),
        Output("login-alert", "is_open"),
        Output("url", "pathname", allow_duplicate=True),
        Input("login-btn", "n_clicks"),
        State("login-email", "value"),
        State("login-password", "value"),
        prevent_initial_call=True,
    )
    def handle_login(n_clicks, email, password):
        if not n_clicks:
            return no_update, no_update, no_update, no_update
        if not email or not password:
            return "Please fill in all fields.", "warning", True, no_update

        # ── Dev bypass (DEV_AUTH_BYPASS=true in .env) ──────────────────────
        if settings.DEV_AUTH_BYPASS:
            uid = DEV_UID_PREFIX + email.strip().replace("@", "-").replace(".", "-")
            flask_session["user_id"] = uid
            flask_session["user_email"] = email.strip()
            flask_session["id_token"] = "dev-token"
            flask_session["refresh_token"] = "dev-refresh"
            flask_session.permanent = True
            _upsert_user(uid, email.strip())
            log.info("[DEV BYPASS] User signed in: %s", email.strip())
            return no_update, no_update, False, "/"

        result = sign_in(email.strip(), password)
        if result.success:
            flask_session["user_id"] = result.uid
            flask_session["user_email"] = result.email
            flask_session["id_token"] = result.id_token
            flask_session["refresh_token"] = result.refresh_token
            flask_session.permanent = True
            _upsert_user(result.uid, result.email)
            log.info("User signed in: %s", result.email)
            return no_update, no_update, False, "/"
        return result.error, "danger", True, no_update

    # ── Signup ─────────────────────────────────────────────────────────────────
    @app.callback(
        Output("signup-alert", "children"),
        Output("signup-alert", "color"),
        Output("signup-alert", "is_open"),
        Output("url", "pathname", allow_duplicate=True),
        Input("signup-btn", "n_clicks"),
        State("signup-email", "value"),
        State("signup-password", "value"),
        State("signup-confirm", "value"),
        prevent_initial_call=True,
    )
    def handle_signup(n_clicks, email, password, confirm):
        if not n_clicks:
            return no_update, no_update, no_update, no_update
        if not email or not password or not confirm:
            return "Please fill in all fields.", "warning", True, no_update
        if password != confirm:
            return "Passwords do not match.", "warning", True, no_update
        if len(password) < 6:
            return "Password must be at least 6 characters.", "warning", True, no_update

        # ── Dev bypass ──────────────────────────────────────────────────────
        if settings.DEV_AUTH_BYPASS:
            uid = DEV_UID_PREFIX + email.strip().replace("@", "-").replace(".", "-")
            flask_session["user_id"] = uid
            flask_session["user_email"] = email.strip()
            flask_session["id_token"] = "dev-token"
            flask_session["refresh_token"] = "dev-refresh"
            flask_session.permanent = True
            _upsert_user(uid, email.strip())
            log.info("[DEV BYPASS] New user: %s", email.strip())
            return no_update, no_update, False, "/"

        result = sign_up(email.strip(), password)
        if result.success:
            flask_session["user_id"] = result.uid
            flask_session["user_email"] = result.email
            flask_session["id_token"] = result.id_token
            flask_session["refresh_token"] = result.refresh_token
            flask_session.permanent = True
            _upsert_user(result.uid, result.email)
            log.info("New user registered: %s", result.email)
            return no_update, no_update, False, "/"
        return result.error, "danger", True, no_update

    # ── Password Reset ─────────────────────────────────────────────────────────
    @app.callback(
        Output("reset-alert", "children"),
        Output("reset-alert", "color"),
        Output("reset-alert", "is_open"),
        Input("reset-btn", "n_clicks"),
        State("reset-email", "value"),
        prevent_initial_call=True,
    )
    def handle_reset(n_clicks, email):
        if not n_clicks:
            return no_update, no_update, no_update
        if not email:
            return "Please enter your email address.", "warning", True

        result = send_password_reset(email.strip())
        if result.success:
            return "Password reset email sent! Check your inbox.", "success", True
        return result.error, "danger", True
