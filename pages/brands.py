"""Brand Management page layout."""

import dash_bootstrap_components as dbc
from dash import html, dcc

from components.common import page_header, empty_state, confirm_modal

INDUSTRY_OPTIONS = [
    "Technology", "Retail & E-commerce", "Food & Beverage",
    "Health & Wellness", "Finance & Banking", "Fashion & Apparel",
    "Travel & Hospitality", "Education", "Media & Entertainment",
    "Real Estate", "Automotive", "Non-Profit", "Other",
]

TONE_OPTIONS = [
    "Professional", "Friendly", "Playful", "Bold & Edgy",
    "Inspirational", "Minimalist", "Luxurious", "Technical",
]


def _brand_form(prefix: str = "brand") -> list:
    """Reusable brand form fields for create/edit modals."""
    return [
        dbc.Label("Brand Name *", className="form-label-custom"),
        dbc.Input(id=f"{prefix}-name", placeholder="e.g. Acme Corp", className="form-input-custom mb-2"),

        dbc.Label("Industry", className="form-label-custom mt-2"),
        dbc.Select(
            id=f"{prefix}-industry",
            options=[{"label": o, "value": o} for o in INDUSTRY_OPTIONS],
            placeholder="Select industry…",
            className="form-input-custom mb-2",
        ),

        dbc.Label("Brand Tone", className="form-label-custom mt-2"),
        dbc.Select(
            id=f"{prefix}-tone",
            options=[{"label": o, "value": o} for o in TONE_OPTIONS],
            placeholder="Select tone…",
            className="form-input-custom mb-2",
        ),

        dbc.Label("Brand Description", className="form-label-custom mt-2"),
        dbc.Textarea(
            id=f"{prefix}-description",
            placeholder="What does this brand stand for?",
            className="form-input-custom mb-2",
            rows=3,
        ),

        dbc.Label("Target Audience", className="form-label-custom mt-2"),
        dbc.Textarea(
            id=f"{prefix}-audience",
            placeholder="Describe your ideal customer",
            className="form-input-custom mb-2",
            rows=2,
        ),

        dbc.Label("Brand Guidelines", className="form-label-custom mt-2"),
        dbc.Textarea(
            id=f"{prefix}-guidelines",
            placeholder="Key brand guidelines (colours, voice, do's and don'ts)",
            className="form-input-custom mb-2",
            rows=3,
        ),

        dbc.Label("Website", className="form-label-custom mt-2"),
        dbc.Input(
            id=f"{prefix}-website",
            type="url",
            placeholder="https://example.com",
            className="form-input-custom mb-2",
        ),
    ]


def brands_layout() -> html.Div:
    return html.Div(
        [
            dcc.Store(id="brands-store", data=[]),
            dcc.Store(id="brand-edit-id", data=None),
            dcc.Store(id="brands-reload-trigger", data=0),

            page_header(
                title="Brand Management",
                subtitle="Create and manage your brand profiles.",
                action_button=dbc.Button(
                    [html.I(className="bi bi-plus-lg me-1"), "New Brand"],
                    id="open-create-brand-modal",
                    color="primary",
                    className="btn-primary-custom",
                    n_clicks=0,
                ),
            ),

            # Search & Filter bar
            dbc.Row(
                [
                    dbc.Col(
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText(html.I(className="bi bi-search")),
                                dbc.Input(
                                    id="brand-search",
                                    placeholder="Search brands…",
                                    debounce=True,
                                    className="form-input-custom",
                                ),
                            ],
                        ),
                        md=5, className="mb-2",
                    ),
                    dbc.Col(
                        dbc.Select(
                            id="brand-filter-industry",
                            options=[{"label": "All Industries", "value": ""}]
                            + [{"label": o, "value": o} for o in INDUSTRY_OPTIONS],
                            value="",
                            className="form-input-custom",
                        ),
                        md=3, className="mb-2",
                    ),
                ],
                className="mb-3 align-items-center",
            ),

            # Alert area
            html.Div(id="brands-alert"),

            # Brand grid
            html.Div(id="brands-grid", className="brands-grid"),

            # ── Create Modal ──────────────────────────────────────────────────
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle([html.I(className="bi bi-bookmark-star-fill me-2"), "Create Brand"])),
                    dbc.ModalBody(
                        [
                            dbc.Alert(id="create-brand-alert", is_open=False, dismissable=True, className="app-alert"),
                            *_brand_form("create-brand"),
                        ]
                    ),
                    dbc.ModalFooter(
                        [
                            dbc.Button("Cancel", id="close-create-brand-modal", color="secondary", outline=True, n_clicks=0),
                            dbc.Button("Create Brand", id="save-create-brand", color="primary", className="btn-primary-custom", n_clicks=0),
                        ]
                    ),
                ],
                id="create-brand-modal",
                is_open=False,
                size="lg",
                scrollable=True,
            ),

            # ── Edit Modal ────────────────────────────────────────────────────
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle([html.I(className="bi bi-pencil-fill me-2"), "Edit Brand"])),
                    dbc.ModalBody(
                        [
                            dbc.Alert(id="edit-brand-alert", is_open=False, dismissable=True, className="app-alert"),
                            *_brand_form("edit-brand"),
                        ]
                    ),
                    dbc.ModalFooter(
                        [
                            dbc.Button("Cancel", id="close-edit-brand-modal", color="secondary", outline=True, n_clicks=0),
                            dbc.Button("Save Changes", id="save-edit-brand", color="primary", className="btn-primary-custom", n_clicks=0),
                        ]
                    ),
                ],
                id="edit-brand-modal",
                is_open=False,
                size="lg",
                scrollable=True,
            ),

            # ── Delete Confirm ────────────────────────────────────────────────
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Delete Brand")),
                    dbc.ModalBody("Are you sure you want to delete this brand? This will also delete all associated campaigns. This action cannot be undone."),
                    dbc.ModalFooter(
                        [
                            dbc.Button("Cancel", id="cancel-delete-brand", color="secondary", outline=True, n_clicks=0),
                            dbc.Button("Delete", id="confirm-delete-brand", color="danger", n_clicks=0),
                        ]
                    ),
                ],
                id="delete-brand-modal",
                is_open=False,
                centered=True,
            ),

            dcc.Store(id="brand-delete-id", data=None),
        ],
        className="page-content",
    )


def brand_card(brand: dict) -> dbc.Card:
    """Render a brand as a card in the grid."""
    industry = brand.get("industry") or "General"
    initials = "".join(w[0].upper() for w in brand["brand_name"].split()[:2])
    campaign_count = brand.get("campaign_count", 0)

    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.Div(
                        [
                            html.Div(
                                initials,
                                className="brand-avatar",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H5(brand["brand_name"], className="brand-card-name"),
                                            html.Span(industry, className="brand-card-industry"),
                                        ],
                                        className="brand-card-title-row",
                                    ),
                                    html.P(
                                        brand.get("brand_description") or "No description.",
                                        className="brand-card-desc",
                                    ),
                                ],
                                className="brand-card-info",
                            ),
                        ],
                        className="brand-card-top",
                    ),

                    html.Hr(className="brand-card-divider"),

                    html.Div(
                        [
                            html.Span(
                                [html.I(className="bi bi-megaphone me-1"), f"{campaign_count} campaign{'s' if campaign_count != 1 else ''}"],
                                className="brand-card-meta",
                            ),
                            html.Div(
                                [
                                    dbc.Button(
                                        html.I(className="bi bi-pencil-fill"),
                                        id={"type": "edit-brand-btn", "index": brand["id"]},
                                        size="sm",
                                        color="light",
                                        className="card-action-btn",
                                        title="Edit brand",
                                        n_clicks=0,
                                    ),
                                    dbc.Button(
                                        html.I(className="bi bi-trash-fill"),
                                        id={"type": "delete-brand-btn", "index": brand["id"]},
                                        size="sm",
                                        color="light",
                                        className="card-action-btn card-action-btn--danger",
                                        title="Delete brand",
                                        n_clicks=0,
                                    ),
                                ],
                                className="brand-card-actions",
                            ),
                        ],
                        className="brand-card-footer",
                    ),
                ]
            ),
        ],
        className="brand-card",
    )
