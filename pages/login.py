"""Login, Signup, and Password Reset page layouts."""

import dash_bootstrap_components as dbc
from dash import html, dcc


def _auth_card(content: list) -> html.Div:
    return html.Div(
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            html.Span("AI", className="auth-logo-text"),
                            className="auth-logo-mark",
                        ),
                        html.H1("Creative AI Studio", className="auth-brand"),
                        html.P("AI-powered marketing platform", className="auth-tagline"),
                    ],
                    className="auth-brand-section",
                ),
                *content,
            ],
            className="auth-card",
        ),
        className="auth-wrapper",
    )


# ── Login Layout ──────────────────────────────────────────────────────────────

def login_layout() -> html.Div:
    return _auth_card([
        html.H3("Welcome back", className="auth-heading"),
        html.P("Sign in to continue", className="auth-subheading"),
        dbc.Alert(id="login-alert", is_open=False, dismissable=True, className="app-alert"),
        dbc.Form(
            [
                dbc.Label("Email address", html_for="login-email", className="form-label-custom"),
                dbc.Input(
                    id="login-email",
                    type="email",
                    placeholder="you@example.com",
                    className="form-input-custom",
                    autocomplete="email",
                    debounce=False,
                    n_submit=0,
                ),
                dbc.Label("Password", html_for="login-password", className="form-label-custom mt-3"),
                dbc.Input(
                    id="login-password",
                    type="password",
                    placeholder="Your password",
                    className="form-input-custom",
                    autocomplete="current-password",
                    debounce=False,
                    n_submit=0,
                ),
                html.Div(
                    html.A("Forgot password?", href="/reset-password", className="auth-link"),
                    className="text-end mt-1",
                ),
                dbc.Button(
                    [html.Span("Sign In", id="login-btn-text"), dbc.Spinner(size="sm", id="login-spinner", spinner_style={"display": "none"})],
                    id="login-btn",
                    color="primary",
                    className="auth-submit-btn mt-3",
                    n_clicks=0,
                ),
            ],
            id="login-form",
        ),
        html.Div(
            [
                html.Span("Don't have an account? "),
                html.A("Sign up", href="/signup", className="auth-link"),
            ],
            className="auth-footer-text",
        ),
    ])


# ── Signup Layout ─────────────────────────────────────────────────────────────

def signup_layout() -> html.Div:
    return _auth_card([
        html.H3("Create an account", className="auth-heading"),
        html.P("Start building AI-powered campaigns", className="auth-subheading"),
        dbc.Alert(id="signup-alert", is_open=False, dismissable=True, className="app-alert"),
        dbc.Form(
            [
                dbc.Label("Email address", html_for="signup-email", className="form-label-custom"),
                dbc.Input(
                    id="signup-email",
                    type="email",
                    placeholder="you@example.com",
                    className="form-input-custom",
                    autocomplete="email",
                    n_submit=0,
                ),
                dbc.Label("Password", html_for="signup-password", className="form-label-custom mt-3"),
                dbc.Input(
                    id="signup-password",
                    type="password",
                    placeholder="Minimum 6 characters",
                    className="form-input-custom",
                    autocomplete="new-password",
                    n_submit=0,
                ),
                dbc.Label("Confirm Password", html_for="signup-confirm", className="form-label-custom mt-3"),
                dbc.Input(
                    id="signup-confirm",
                    type="password",
                    placeholder="Repeat your password",
                    className="form-input-custom",
                    autocomplete="new-password",
                    n_submit=0,
                ),
                dbc.Button(
                    "Create Account",
                    id="signup-btn",
                    color="primary",
                    className="auth-submit-btn mt-3",
                    n_clicks=0,
                ),
            ],
            id="signup-form",
        ),
        html.Div(
            [
                html.Span("Already have an account? "),
                html.A("Sign in", href="/login", className="auth-link"),
            ],
            className="auth-footer-text",
        ),
    ])


# ── Reset Password Layout ─────────────────────────────────────────────────────

def reset_layout() -> html.Div:
    return _auth_card([
        html.H3("Reset your password", className="auth-heading"),
        html.P("We'll send you a reset link", className="auth-subheading"),
        dbc.Alert(id="reset-alert", is_open=False, dismissable=True, className="app-alert"),
        dbc.Form(
            [
                dbc.Label("Email address", html_for="reset-email", className="form-label-custom"),
                dbc.Input(
                    id="reset-email",
                    type="email",
                    placeholder="you@example.com",
                    className="form-input-custom",
                    autocomplete="email",
                    n_submit=0,
                ),
                dbc.Button(
                    "Send Reset Email",
                    id="reset-btn",
                    color="primary",
                    className="auth-submit-btn mt-3",
                    n_clicks=0,
                ),
            ],
            id="reset-form",
        ),
        html.Div(
            html.A("← Back to sign in", href="/login", className="auth-link"),
            className="auth-footer-text",
        ),
    ])
