"""Campaign Management page layout."""

import dash_bootstrap_components as dbc
from dash import html, dcc

from components.common import page_header, badge_status

OBJECTIVE_OPTIONS = [
    "Brand Awareness", "Lead Generation", "Sales Conversion",
    "Customer Retention", "Product Launch", "Community Building",
    "Website Traffic", "App Downloads",
]


def _campaign_form(prefix: str = "campaign", brand_options: list = None) -> list:
    brand_options = brand_options or []
    return [
        dbc.Label("Campaign Name *", className="form-label-custom"),
        dbc.Input(id=f"{prefix}-name", placeholder="e.g. Summer Sale 2025", className="form-input-custom mb-2"),

        dbc.Label("Brand *", className="form-label-custom mt-2"),
        dbc.Select(
            id=f"{prefix}-brand",
            options=brand_options,
            placeholder="Select a brand…",
            className="form-input-custom mb-2",
        ),

        dbc.Label("Campaign Objective", className="form-label-custom mt-2"),
        dbc.Select(
            id=f"{prefix}-objective",
            options=[{"label": o, "value": o} for o in OBJECTIVE_OPTIONS],
            placeholder="Select objective…",
            className="form-input-custom mb-2",
        ),

        dbc.Label("Campaign Theme", className="form-label-custom mt-2"),
        dbc.Input(id=f"{prefix}-theme", placeholder="e.g. Back to School", className="form-input-custom mb-2"),

        dbc.Label("Description", className="form-label-custom mt-2"),
        dbc.Textarea(
            id=f"{prefix}-description",
            placeholder="What is this campaign about?",
            className="form-input-custom mb-2",
            rows=3,
        ),

        dbc.Label("Target Audience", className="form-label-custom mt-2"),
        dbc.Textarea(
            id=f"{prefix}-audience",
            placeholder="Who are you trying to reach?",
            className="form-input-custom mb-2",
            rows=2,
        ),

        dbc.Label("Keywords", className="form-label-custom mt-2"),
        dbc.Input(
            id=f"{prefix}-keywords",
            placeholder="e.g. summer, sale, discount (comma-separated)",
            className="form-input-custom mb-2",
        ),

        dbc.Label("Content Pillars", className="form-label-custom mt-2"),
        dbc.Input(
            id=f"{prefix}-pillars",
            placeholder="e.g. Education, Entertainment, Promotion (comma-separated)",
            className="form-input-custom mb-2",
        ),

        dbc.Label("Status", className="form-label-custom mt-2"),
        dbc.RadioItems(
            id=f"{prefix}-status",
            options=[
                {"label": "Draft", "value": "draft"},
                {"label": "Active", "value": "active"},
            ],
            value="draft",
            inline=True,
            className="mt-1",
        ),
    ]


def campaigns_layout() -> html.Div:
    return html.Div(
        [
            dcc.Store(id="campaigns-store", data=[]),
            dcc.Store(id="campaign-edit-id", data=None),
            dcc.Store(id="campaign-delete-id", data=None),
            dcc.Store(id="campaign-brands-store", data=[]),
            dcc.Store(id="campaigns-reload-trigger", data=0),

            page_header(
                title="Campaign Management",
                subtitle="Create, manage, and track all your campaigns.",
                action_button=dbc.Button(
                    [html.I(className="bi bi-plus-lg me-1"), "New Campaign"],
                    id="open-create-campaign-modal",
                    color="primary",
                    className="btn-primary-custom",
                    n_clicks=0,
                ),
            ),

            # Filter bar
            dbc.Row(
                [
                    dbc.Col(
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText(html.I(className="bi bi-search")),
                                dbc.Input(
                                    id="campaign-search",
                                    placeholder="Search campaigns…",
                                    debounce=True,
                                    className="form-input-custom",
                                ),
                            ]
                        ),
                        md=5, className="mb-2",
                    ),
                    dbc.Col(
                        dbc.Select(
                            id="campaign-filter-brand",
                            options=[{"label": "All Brands", "value": ""}],
                            value="",
                            className="form-input-custom",
                        ),
                        md=3, className="mb-2",
                    ),
                    dbc.Col(
                        dbc.Select(
                            id="campaign-filter-status",
                            options=[
                                {"label": "All Status", "value": ""},
                                {"label": "Active", "value": "active"},
                                {"label": "Draft", "value": "draft"},
                            ],
                            value="",
                            className="form-input-custom",
                        ),
                        md=2, className="mb-2",
                    ),
                ],
                className="mb-3 align-items-center",
            ),

            html.Div(id="campaigns-alert"),

            # Campaign list
            html.Div(id="campaigns-list", className="campaigns-list"),

            # ── Create Modal ──────────────────────────────────────────────────
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle([html.I(className="bi bi-megaphone-fill me-2"), "Create Campaign"])),
                    dbc.ModalBody(
                        [
                            dbc.Alert(id="create-campaign-alert", is_open=False, dismissable=True, className="app-alert"),
                            *_campaign_form("create-campaign"),
                        ]
                    ),
                    dbc.ModalFooter(
                        [
                            dbc.Button("Cancel", id="close-create-campaign-modal", color="secondary", outline=True, n_clicks=0),
                            dbc.Button("Create Campaign", id="save-create-campaign", color="primary", className="btn-primary-custom", n_clicks=0),
                        ]
                    ),
                ],
                id="create-campaign-modal",
                is_open=False,
                size="lg",
                scrollable=True,
            ),

            # ── Edit Modal ────────────────────────────────────────────────────
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle([html.I(className="bi bi-pencil-fill me-2"), "Edit Campaign"])),
                    dbc.ModalBody(
                        [
                            dbc.Alert(id="edit-campaign-alert", is_open=False, dismissable=True, className="app-alert"),
                            *_campaign_form("edit-campaign"),
                        ]
                    ),
                    dbc.ModalFooter(
                        [
                            dbc.Button("Cancel", id="close-edit-campaign-modal", color="secondary", outline=True, n_clicks=0),
                            dbc.Button("Save Changes", id="save-edit-campaign", color="primary", className="btn-primary-custom", n_clicks=0),
                        ]
                    ),
                ],
                id="edit-campaign-modal",
                is_open=False,
                size="lg",
                scrollable=True,
            ),

            # ── Delete Confirm ────────────────────────────────────────────────
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Delete Campaign")),
                    dbc.ModalBody("Are you sure you want to delete this campaign? This action cannot be undone."),
                    dbc.ModalFooter(
                        [
                            dbc.Button("Cancel", id="cancel-delete-campaign", color="secondary", outline=True, n_clicks=0),
                            dbc.Button("Delete", id="confirm-delete-campaign", color="danger", n_clicks=0),
                        ]
                    ),
                ],
                id="delete-campaign-modal",
                is_open=False,
                centered=True,
            ),
        ],
        className="page-content",
    )


def campaign_row(campaign: dict) -> html.Div:
    """Render a single campaign row in the campaign list."""
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        html.I(className="bi bi-megaphone-fill campaign-row-icon"),
                        className="campaign-row-icon-wrap",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Strong(campaign["campaign_name"], className="campaign-row-name"),
                                    badge_status(campaign["status"]),
                                ],
                                className="campaign-row-title",
                            ),
                            html.Span(
                                [
                                    html.I(className="bi bi-bookmark me-1"),
                                    campaign.get("brand_name", ""),
                                    html.Span(" · ", className="mx-1"),
                                    html.I(className="bi bi-bullseye me-1"),
                                    campaign.get("campaign_objective") or "No objective set",
                                ],
                                className="campaign-row-meta",
                            ),
                        ],
                        className="campaign-row-info",
                    ),
                ],
                className="campaign-row-left",
            ),
            html.Div(
                [
                    dbc.Button(
                        html.I(className="bi bi-pencil-fill"),
                        id={"type": "edit-campaign-btn", "index": campaign["id"]},
                        size="sm",
                        color="light",
                        className="card-action-btn me-1",
                        title="Edit campaign",
                        n_clicks=0,
                    ),
                    dbc.Button(
                        html.I(className="bi bi-trash-fill"),
                        id={"type": "delete-campaign-btn", "index": campaign["id"]},
                        size="sm",
                        color="light",
                        className="card-action-btn card-action-btn--danger",
                        title="Delete campaign",
                        n_clicks=0,
                    ),
                ],
                className="campaign-row-actions",
            ),
        ],
        className="campaign-row",
    )
