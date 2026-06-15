import dash_bootstrap_components as dbc
from dash import html


NAV_ITEMS = [
    {"href": "/", "icon": "bi bi-grid-1x2-fill", "label": "Dashboard"},
    {"href": "/brands", "icon": "bi bi-bookmark-star-fill", "label": "Brands"},
    {"href": "/campaigns", "icon": "bi bi-megaphone-fill", "label": "Campaigns"},
    {"href": "/studio", "icon": "bi bi-magic", "label": "Campaign Studio"},
    {"href": "/settings", "icon": "bi bi-gear-fill", "label": "Settings"},
]


def render_sidebar(current_path: str = "/") -> html.Div:
    nav_links = []
    for item in NAV_ITEMS:
        is_active = (
            current_path == item["href"]
            if item["href"] != "/"
            else current_path in ("/", "")
        )
        nav_links.append(
            html.A(
                [
                    html.I(className=item["icon"] + " sidebar-nav-icon"),
                    html.Span(item["label"], className="sidebar-nav-label"),
                ],
                href=item["href"],
                className=f"sidebar-nav-item{'  sidebar-nav-item--active' if is_active else ''}",
            )
        )

    return html.Div(
        [
            # Logo / brand
            html.Div(
                [
                    html.Div(
                        html.Span("AI", className="sidebar-logo-text"),
                        className="sidebar-logo-mark",
                    ),
                    html.Span("Creative AI Studio", className="sidebar-brand-name"),
                ],
                className="sidebar-header",
            ),
            html.Hr(className="sidebar-divider"),
            # Navigation
            html.Nav(nav_links, className="sidebar-nav"),
            # Footer
            html.Div(
                html.Span("Powered by Google Cloud", className="sidebar-footer-text"),
                className="sidebar-footer",
            ),
        ],
        className="sidebar",
        id="sidebar",
    )
