"""Shared UI building blocks used across pages."""

import dash_bootstrap_components as dbc
from dash import html


def stat_card(title: str, value, icon: str, color: str = "primary", subtitle: str = "") -> dbc.Card:
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.P(title, className="stat-card-title"),
                                html.H2(str(value), className="stat-card-value"),
                                html.P(subtitle, className="stat-card-subtitle") if subtitle else None,
                            ],
                            className="stat-card-content",
                        ),
                        html.Div(
                            html.I(className=f"bi {icon} stat-card-icon"),
                            className=f"stat-card-icon-wrap stat-card-icon-wrap--{color}",
                        ),
                    ],
                    className="stat-card-inner",
                )
            ]
        ),
        className=f"stat-card stat-card--{color}",
    )


def page_header(title: str, subtitle: str = "", action_button=None) -> html.Div:
    return html.Div(
        [
            html.Div(
                [
                    html.H2(title, className="page-heading"),
                    html.P(subtitle, className="page-subheading") if subtitle else None,
                ],
            ),
            action_button or html.Div(),
        ],
        className="page-header-row",
    )


def empty_state(icon: str, title: str, message: str, action=None) -> html.Div:
    return html.Div(
        [
            html.I(className=f"bi {icon} empty-icon"),
            html.H5(title, className="empty-title"),
            html.P(message, className="empty-message"),
            action or html.Div(),
        ],
        className="empty-state",
    )


def alert_success(message: str) -> dbc.Alert:
    return dbc.Alert(
        [html.I(className="bi bi-check-circle-fill me-2"), message],
        color="success",
        dismissable=True,
        className="app-alert",
    )


def alert_error(message: str) -> dbc.Alert:
    return dbc.Alert(
        [html.I(className="bi bi-exclamation-triangle-fill me-2"), message],
        color="danger",
        dismissable=True,
        className="app-alert",
    )


def badge_status(status: str) -> html.Span:
    cls = "badge-status"
    if status == "active":
        cls += " badge-status--active"
    elif status == "draft":
        cls += " badge-status--draft"
    return html.Span(status.capitalize(), className=cls)


def confirm_modal(modal_id: str, title: str, body: str, confirm_id: str) -> dbc.Modal:
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle(title)),
            dbc.ModalBody(body),
            dbc.ModalFooter(
                [
                    dbc.Button("Cancel", id=f"{modal_id}-cancel", color="secondary", outline=True),
                    dbc.Button("Delete", id=confirm_id, color="danger"),
                ]
            ),
        ],
        id=modal_id,
        is_open=False,
        centered=True,
    )


def step_indicator(steps: list[str], current: int) -> html.Div:
    """Visual multi-step progress indicator. current is 1-indexed."""
    items = []
    for i, label in enumerate(steps, start=1):
        if i < current:
            state = "completed"
            icon = html.I(className="bi bi-check-lg")
        elif i == current:
            state = "active"
            icon = html.Span(str(i))
        else:
            state = "pending"
            icon = html.Span(str(i))

        items.append(
            html.Div(
                [
                    html.Div(icon, className=f"step-circle step-circle--{state}"),
                    html.Span(label, className=f"step-label step-label--{state}"),
                ],
                className="step-item",
            )
        )
        if i < len(steps):
            items.append(html.Div(className=f"step-connector{'  step-connector--done' if i < current else ''}"))

    return html.Div(items, className="step-indicator")
