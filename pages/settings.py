"""User Settings page layout."""

import dash_bootstrap_components as dbc
from dash import html, dcc


def settings_layout(user_email: str = "") -> html.Div:
    return html.Div(
        [
            html.H2("Settings", className="page-heading"),
            html.P("Manage your account and application preferences.", className="page-subheading mb-4"),

            dbc.Row(
                [
                    dbc.Col(
                        [
                            # Account Info
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        [html.I(className="bi bi-person-fill me-2"), "Account Information"],
                                        className="card-section-header",
                                    ),
                                    dbc.CardBody(
                                        [
                                            html.Div(id="settings-alert"),
                                            dbc.Label("Email Address", className="form-label-custom"),
                                            dbc.Input(
                                                value=user_email,
                                                disabled=True,
                                                className="form-input-custom mb-3",
                                            ),
                                            dbc.Label("Account Status", className="form-label-custom"),
                                            html.Div(
                                                [
                                                    html.Span(
                                                        [html.I(className="bi bi-circle-fill me-1 text-success"), "Active"],
                                                        className="badge-status badge-status--active",
                                                    )
                                                ],
                                                className="mb-3",
                                            ),
                                            html.Hr(),
                                            html.H6("Change Password", className="mb-3"),
                                            dbc.Label("New Password", className="form-label-custom"),
                                            dbc.Input(
                                                id="settings-new-password",
                                                type="password",
                                                placeholder="Minimum 6 characters",
                                                className="form-input-custom mb-2",
                                            ),
                                            dbc.Button(
                                                "Send Password Reset Email",
                                                id="settings-reset-pw-btn",
                                                color="secondary",
                                                outline=True,
                                                className="mt-1",
                                                n_clicks=0,
                                            ),
                                        ]
                                    ),
                                ],
                                className="content-card mb-3",
                            ),
                        ],
                        md=6,
                    ),

                    dbc.Col(
                        [
                            # GCP Integration Status
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        [html.I(className="bi bi-cloud-fill me-2"), "Google Cloud Integration"],
                                        className="card-section-header",
                                    ),
                                    dbc.CardBody(
                                        [
                                            _integration_row("bi-database-fill", "Cloud SQL (PostgreSQL)", True),
                                            _integration_row("bi-cloud-arrow-up-fill", "Cloud Storage (GCS)", True),
                                            _integration_row("bi-shield-lock-fill", "Google Identity Platform", True),
                                            _integration_row("bi-cpu-fill", "Vertex AI", False, note="Coming soon"),
                                            _integration_row("bi-image-fill", "Imagen API", False, note="Coming soon"),
                                        ]
                                    ),
                                ],
                                className="content-card mb-3",
                            ),

                            # Danger Zone
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        [html.I(className="bi bi-exclamation-triangle-fill me-2 text-danger"), "Danger Zone"],
                                        className="card-section-header",
                                    ),
                                    dbc.CardBody(
                                        [
                                            html.P(
                                                "Sign out of Creative AI Studio on this device.",
                                                className="text-muted mb-3",
                                            ),
                                            html.A(
                                                [html.I(className="bi bi-box-arrow-right me-1"), "Sign Out"],
                                                href="/logout",
                                                className="btn btn-outline-danger btn-sm",
                                            ),
                                        ]
                                    ),
                                ],
                                className="content-card",
                            ),
                        ],
                        md=6,
                    ),
                ],
                className="g-3",
            ),
        ],
        className="page-content",
    )


def _integration_row(icon: str, name: str, enabled: bool, note: str = "") -> html.Div:
    return html.Div(
        [
            html.I(className=f"bi {icon} integration-icon"),
            html.Span(name, className="integration-name"),
            html.Span(
                note if note else ("Enabled" if enabled else "Disabled"),
                className=f"integration-status {'integration-status--on' if enabled else 'integration-status--off'}",
            ),
        ],
        className="integration-row",
    )
