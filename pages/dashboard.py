"""Dashboard page layout."""

import dash_bootstrap_components as dbc
from dash import html, dcc

from components.common import stat_card, page_header, empty_state


def dashboard_layout(user_email: str = "") -> html.Div:
    first_name = user_email.split("@")[0].capitalize() if user_email else "there"

    return html.Div(
        [
            dcc.Store(id="dashboard-stats-store"),
            dcc.Interval(id="dashboard-refresh", interval=30_000, n_intervals=0),

            page_header(
                title=f"Welcome, {first_name}!",
                subtitle="Here's what's happening with your campaigns.",
            ),

            # Stats row
            dbc.Row(
                [
                    dbc.Col(
                        stat_card("Total Brands", 0, "bi-bookmark-star-fill", "primary"),
                        id="stat-brands",
                        xs=12, sm=6, xl=3, className="mb-3",
                    ),
                    dbc.Col(
                        stat_card("Total Campaigns", 0, "bi-megaphone-fill", "violet"),
                        id="stat-campaigns",
                        xs=12, sm=6, xl=3, className="mb-3",
                    ),
                    dbc.Col(
                        stat_card("Active Campaigns", 0, "bi-lightning-charge-fill", "success"),
                        id="stat-active",
                        xs=12, sm=6, xl=3, className="mb-3",
                    ),
                    dbc.Col(
                        stat_card("Drafts", 0, "bi-file-earmark-text-fill", "warning"),
                        id="stat-drafts",
                        xs=12, sm=6, xl=3, className="mb-3",
                    ),
                ],
                className="g-3 mb-4",
            ),

            # Quick Actions + Recent Activity
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    html.H5("Quick Actions", className="card-section-title"),
                                    className="card-section-header",
                                ),
                                dbc.CardBody(
                                    [
                                        html.A(
                                            [
                                                html.Div(
                                                    html.I(className="bi bi-magic quick-action-icon"),
                                                    className="quick-action-icon-wrap quick-action-icon-wrap--primary",
                                                ),
                                                html.Div(
                                                    [
                                                        html.Strong("New Campaign"),
                                                        html.P("Launch the Campaign Studio", className="quick-action-desc"),
                                                    ]
                                                ),
                                                html.I(className="bi bi-chevron-right ms-auto"),
                                            ],
                                            href="/studio",
                                            className="quick-action-item",
                                        ),
                                        html.A(
                                            [
                                                html.Div(
                                                    html.I(className="bi bi-bookmark-plus quick-action-icon"),
                                                    className="quick-action-icon-wrap quick-action-icon-wrap--violet",
                                                ),
                                                html.Div(
                                                    [
                                                        html.Strong("New Brand"),
                                                        html.P("Create a new brand profile", className="quick-action-desc"),
                                                    ]
                                                ),
                                                html.I(className="bi bi-chevron-right ms-auto"),
                                            ],
                                            href="/brands",
                                            className="quick-action-item",
                                        ),
                                        html.A(
                                            [
                                                html.Div(
                                                    html.I(className="bi bi-megaphone quick-action-icon"),
                                                    className="quick-action-icon-wrap quick-action-icon-wrap--success",
                                                ),
                                                html.Div(
                                                    [
                                                        html.Strong("View Campaigns"),
                                                        html.P("Manage all your campaigns", className="quick-action-desc"),
                                                    ]
                                                ),
                                                html.I(className="bi bi-chevron-right ms-auto"),
                                            ],
                                            href="/campaigns",
                                            className="quick-action-item",
                                        ),
                                    ]
                                ),
                            ],
                            className="content-card h-100",
                        ),
                        lg=4, className="mb-3",
                    ),

                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    html.H5("Recent Campaigns", className="card-section-title"),
                                    className="card-section-header",
                                ),
                                dbc.CardBody(
                                    html.Div(id="recent-campaigns-list"),
                                ),
                            ],
                            className="content-card h-100",
                        ),
                        lg=8, className="mb-3",
                    ),
                ],
                className="g-3",
            ),
        ],
        className="page-content",
    )
