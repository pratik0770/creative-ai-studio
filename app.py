"""Creative AI Studio — Main Dash Application Entry Point."""

import os
from datetime import timedelta

import dash
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output, State, no_update
from flask import Flask, session as flask_session, redirect, request, jsonify
from flask_session import Session

from cloud.logging_config import setup_logging, get_logger
from config.settings import settings

# ── Logging must be first ──────────────────────────────────────────────────────
setup_logging()
log = get_logger(__name__)

# ── Flask server ───────────────────────────────────────────────────────────────
server = Flask(__name__)
server.config["SECRET_KEY"] = settings.SECRET_KEY
server.config["SESSION_TYPE"] = settings.SESSION_TYPE
server.config["SESSION_PERMANENT"] = settings.SESSION_PERMANENT
server.config["PERMANENT_SESSION_LIFETIME"] = timedelta(seconds=settings.PERMANENT_SESSION_LIFETIME)
server.config["SESSION_FILE_DIR"] = os.path.join(os.path.dirname(__file__), "flask_session")

os.makedirs(server.config["SESSION_FILE_DIR"], exist_ok=True)
Session(server)

# ── Dash app ───────────────────────────────────────────────────────────────────
app = Dash(
    __name__,
    server=server,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css",
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap",
    ],
    suppress_callback_exceptions=True,
    title=settings.APP_NAME,
    update_title=None,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {"name": "description", "content": "AI-powered marketing campaign platform"},
    ],
)
app.config.suppress_callback_exceptions = True

# ── Auth pages (public — no session required) ──────────────────────────────────
PUBLIC_PATHS = {"/login", "/signup", "/reset-password"}

# ── Request-level auth guard ───────────────────────────────────────────────────
@server.before_request
def auth_guard():
    path = request.path

    # Always allow: static assets, Dash internals, health check, logout
    skip_prefixes = ("/_dash", "/assets/", "/_reload", "/health", "/logout")
    if any(path.startswith(p) for p in skip_prefixes) or path in PUBLIC_PATHS:
        return None

    if "user_id" not in flask_session:
        # For XHR/JSON requests (Dash callbacks), return 401
        if request.headers.get("Content-Type", "").startswith("application/json"):
            return jsonify({"error": "Unauthorized"}), 401
        return redirect("/login")


@server.route("/health")
def health():
    from database.connection import check_connection
    db_ok = check_connection()
    status = "ok" if db_ok else "degraded"
    return jsonify({"status": status, "db": db_ok}), 200 if db_ok else 503


@server.route("/logout")
def logout():
    flask_session.clear()
    return redirect("/login")


# ── App Layout ─────────────────────────────────────────────────────────────────
app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        html.Div(id="app-content"),
    ]
)


# ── Root routing callback ──────────────────────────────────────────────────────
@app.callback(
    Output("app-content", "children"),
    Input("url", "pathname"),
)
def route(pathname):
    from components.sidebar import render_sidebar
    from components.header import render_header
    from pages.login import login_layout, signup_layout, reset_layout
    from pages.dashboard import dashboard_layout
    from pages.brands import brands_layout
    from pages.campaigns import campaigns_layout
    from pages.studio import studio_layout
    from pages.settings import settings_layout

    uid = flask_session.get("user_id")
    email = flask_session.get("user_email", "")

    # Auth pages (no sidebar)
    if pathname in ("/login", None, "") and not uid:
        return login_layout()
    if pathname == "/signup" and not uid:
        return signup_layout()
    if pathname == "/reset-password":
        return reset_layout()

    # Redirect unauthenticated users
    if not uid:
        return login_layout()

    # Authenticated: resolve page title and content
    PAGE_MAP = {
        "/":             ("Dashboard",        dashboard_layout(email)),
        "/brands":       ("Brand Management", brands_layout()),
        "/campaigns":    ("Campaigns",        campaigns_layout()),
        "/studio":       ("Campaign Studio",  studio_layout()),
        "/settings":     ("Settings",         settings_layout(email)),
    }

    page_title, page_content = PAGE_MAP.get(
        pathname, ("Not Found", html.Div(
            [
                html.H2("404 — Page not found"),
                html.A("← Back to Dashboard", href="/", className="auth-link"),
            ],
            className="page-content",
        ))
    )

    return html.Div(
        [
            render_sidebar(pathname),
            html.Div(
                [
                    render_header(page_title, email),
                    page_content,
                ],
                className="main-area",
            ),
        ],
        id="app-shell",
    )


# ── Register all callbacks ─────────────────────────────────────────────────────
from callbacks.auth import register_auth_callbacks
from callbacks.brands import register_brand_callbacks
from callbacks.campaigns import register_campaign_callbacks
from callbacks.studio import register_studio_callbacks
from callbacks.dashboard import register_dashboard_callbacks

register_auth_callbacks(app)
register_brand_callbacks(app)
register_campaign_callbacks(app)
register_studio_callbacks(app)
register_dashboard_callbacks(app)


# ── Database initialisation on startup ────────────────────────────────────────
def _init_db_safe():
    try:
        from database.init_db import init_db
        init_db()
    except Exception as exc:
        log.warning("DB init skipped (not connected yet): %s", exc)


if __name__ == "__main__":
    _init_db_safe()
    port = int(os.getenv("PORT", 8050))
    log.info("Starting %s on port %d (debug=%s)", settings.APP_NAME, port, settings.DEBUG)
    app.run(
        debug=settings.DEBUG,
        host="0.0.0.0",
        port=port,
        dev_tools_hot_reload=settings.DEBUG,
    )
else:
    # Gunicorn entrypoint
    _init_db_safe()
