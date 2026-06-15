import dash_bootstrap_components as dbc
from dash import html, dcc


def render_header(page_title: str, user_email: str = "") -> html.Div:
    return html.Div(
        [
            html.Div(
                [
                    html.H4(page_title, className="header-title"),
                ],
                className="header-left",
            ),
            html.Div(
                [
                    # User badge
                    html.Div(
                        [
                            html.I(className="bi bi-person-circle header-user-icon"),
                            html.Span(
                                user_email or "User",
                                className="header-user-email",
                                id="header-user-email",
                            ),
                        ],
                        className="header-user",
                    ),
                    # Logout button
                    html.A(
                        [html.I(className="bi bi-box-arrow-right"), " Logout"],
                        href="/logout",
                        className="header-logout-btn",
                        id="logout-link",
                    ),
                ],
                className="header-right",
            ),
        ],
        className="topbar",
    )
