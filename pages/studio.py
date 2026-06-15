"""Campaign Creation Studio — 3-step guided workflow."""

import dash_bootstrap_components as dbc
from dash import html, dcc

from components.common import step_indicator
from pages.brands import INDUSTRY_OPTIONS, TONE_OPTIONS, _brand_form
from pages.campaigns import OBJECTIVE_OPTIONS


def studio_layout() -> html.Div:
    return html.Div(
        [
            # Persistent state across all steps
            dcc.Store(id="studio-step", data=1),
            dcc.Store(id="studio-brand-data", data={}),
            dcc.Store(id="studio-campaign-data", data={}),
            dcc.Store(id="studio-brands-list", data=[]),

            # Page heading
            html.Div(
                [
                    html.H2("Campaign Studio", className="page-heading"),
                    html.P(
                        "Create a campaign in 3 simple steps.",
                        className="page-subheading",
                    ),
                ],
                className="mb-4",
            ),

            # Step indicator
            html.Div(
                id="studio-step-indicator",
                children=step_indicator(["Select Brand", "Campaign Setup", "Review & Create"], 1),
                className="mb-4",
            ),

            # Alert area
            html.Div(id="studio-alert", className="mb-3"),

            # ── Step containers ──────────────────────────────────────────────
            html.Div(id="studio-step-1", children=_step1_layout()),
            html.Div(id="studio-step-2", children=_step2_layout(), style={"display": "none"}),
            html.Div(id="studio-step-3", children=_step3_layout(), style={"display": "none"}),
        ],
        className="page-content",
    )


# ── Step 1: Select or Create Brand ───────────────────────────────────────────

def _step1_layout() -> html.Div:
    return dbc.Card(
        dbc.CardBody(
            [
                html.H4(
                    [html.I(className="bi bi-bookmark-star-fill me-2 text-primary"), "Step 1: Select a Brand"],
                    className="step-card-title",
                ),
                html.P("Choose an existing brand or create a new one for this campaign.", className="text-muted mb-4"),

                # Toggle between select / create
                dbc.RadioItems(
                    id="studio-brand-mode",
                    options=[
                        {"label": " Select existing brand", "value": "select"},
                        {"label": " Create new brand", "value": "create"},
                    ],
                    value="select",
                    inline=True,
                    className="mb-3 studio-mode-toggle",
                    inputClassName="me-1",
                    labelClassName="me-3",
                ),

                # Existing brand selector
                html.Div(
                    [
                        dbc.Label("Your Brands", className="form-label-custom"),
                        dbc.Select(
                            id="studio-brand-select",
                            options=[],
                            placeholder="Select a brand…",
                            className="form-input-custom",
                        ),
                        html.Div(id="studio-brand-preview", className="mt-3"),
                    ],
                    id="studio-select-brand-section",
                ),

                # New brand creation inline
                html.Div(
                    [
                        dbc.Alert(id="studio-create-brand-alert", is_open=False, dismissable=True, className="app-alert"),
                        dbc.Row(
                            [
                                dbc.Col(_brand_form("studio-new-brand"), md=6),
                            ]
                        ),
                    ],
                    id="studio-create-brand-section",
                    style={"display": "none"},
                ),

                html.Div(
                    dbc.Button(
                        ["Next: Campaign Setup ", html.I(className="bi bi-arrow-right")],
                        id="studio-step1-next",
                        color="primary",
                        className="btn-primary-custom mt-4",
                        n_clicks=0,
                    ),
                    className="text-end",
                ),
            ]
        ),
        className="content-card",
    )


# ── Step 2: Campaign Setup ────────────────────────────────────────────────────

def _step2_layout() -> html.Div:
    return dbc.Card(
        dbc.CardBody(
            [
                html.H4(
                    [html.I(className="bi bi-megaphone-fill me-2 text-primary"), "Step 2: Campaign Setup"],
                    className="step-card-title",
                ),
                html.P("Fill in the details for your new campaign.", className="text-muted mb-4"),

                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Campaign Name *", className="form-label-custom"),
                                dbc.Input(id="studio-campaign-name", placeholder="e.g. Summer Sale 2025", className="form-input-custom mb-2"),

                                dbc.Label("Campaign Objective", className="form-label-custom mt-2"),
                                dbc.Select(
                                    id="studio-campaign-objective",
                                    options=[{"label": o, "value": o} for o in OBJECTIVE_OPTIONS],
                                    placeholder="Select objective…",
                                    className="form-input-custom mb-2",
                                ),

                                dbc.Label("Campaign Theme", className="form-label-custom mt-2"),
                                dbc.Input(id="studio-campaign-theme", placeholder="e.g. Back to School", className="form-input-custom mb-2"),

                                dbc.Label("Campaign Description", className="form-label-custom mt-2"),
                                dbc.Textarea(
                                    id="studio-campaign-description",
                                    placeholder="What is this campaign about?",
                                    className="form-input-custom mb-2",
                                    rows=3,
                                ),
                            ],
                            md=6,
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Target Audience", className="form-label-custom"),
                                dbc.Textarea(
                                    id="studio-campaign-audience",
                                    placeholder="Who are you trying to reach?",
                                    className="form-input-custom mb-2",
                                    rows=2,
                                ),

                                dbc.Label("Keywords", className="form-label-custom mt-2"),
                                dbc.Input(
                                    id="studio-campaign-keywords",
                                    placeholder="summer, sale, discount (comma-separated)",
                                    className="form-input-custom mb-2",
                                ),

                                dbc.Label("Content Pillars", className="form-label-custom mt-2"),
                                dbc.Input(
                                    id="studio-campaign-pillars",
                                    placeholder="Education, Entertainment, Promotion",
                                    className="form-input-custom mb-2",
                                ),

                                dbc.Label("Status", className="form-label-custom mt-2"),
                                dbc.RadioItems(
                                    id="studio-campaign-status",
                                    options=[
                                        {"label": "Draft", "value": "draft"},
                                        {"label": "Active", "value": "active"},
                                    ],
                                    value="draft",
                                    inline=True,
                                    className="mt-1",
                                ),
                            ],
                            md=6,
                        ),
                    ]
                ),

                html.Div(
                    [
                        dbc.Button(
                            [html.I(className="bi bi-arrow-left me-1"), "Back"],
                            id="studio-step2-back",
                            color="secondary",
                            outline=True,
                            className="me-2",
                            n_clicks=0,
                        ),
                        dbc.Button(
                            ["Next: Review ", html.I(className="bi bi-arrow-right")],
                            id="studio-step2-next",
                            color="primary",
                            className="btn-primary-custom",
                            n_clicks=0,
                        ),
                    ],
                    className="d-flex justify-content-end mt-4",
                ),
            ]
        ),
        className="content-card",
    )


# ── Step 3: Review & Create ───────────────────────────────────────────────────

def _step3_layout() -> html.Div:
    return dbc.Card(
        dbc.CardBody(
            [
                html.H4(
                    [html.I(className="bi bi-check2-circle me-2 text-success"), "Step 3: Review & Create"],
                    className="step-card-title",
                ),
                html.P("Review your campaign details before saving.", className="text-muted mb-4"),

                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        [html.I(className="bi bi-bookmark-star-fill me-2"), "Brand Summary"],
                                        className="review-section-header",
                                    ),
                                    dbc.CardBody(html.Div(id="studio-review-brand")),
                                ],
                                className="review-card",
                            ),
                            md=6, className="mb-3",
                        ),
                        dbc.Col(
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        [html.I(className="bi bi-megaphone-fill me-2"), "Campaign Summary"],
                                        className="review-section-header",
                                    ),
                                    dbc.CardBody(html.Div(id="studio-review-campaign")),
                                ],
                                className="review-card",
                            ),
                            md=6, className="mb-3",
                        ),
                    ]
                ),

                html.Div(
                    [
                        dbc.Button(
                            [html.I(className="bi bi-arrow-left me-1"), "Back"],
                            id="studio-step3-back",
                            color="secondary",
                            outline=True,
                            className="me-2",
                            n_clicks=0,
                        ),
                        dbc.Button(
                            [html.I(className="bi bi-floppy-fill me-1"), "Save as Draft"],
                            id="studio-save-draft",
                            color="secondary",
                            className="me-2",
                            n_clicks=0,
                        ),
                        dbc.Button(
                            [html.I(className="bi bi-rocket-takeoff-fill me-1"), "Create Campaign"],
                            id="studio-create-campaign",
                            color="success",
                            className="btn-success-custom",
                            n_clicks=0,
                        ),
                    ],
                    className="d-flex justify-content-end mt-4",
                ),
            ]
        ),
        className="content-card",
    )


def brand_preview_card(brand: dict) -> html.Div:
    """Preview card shown after brand selection in Step 1."""
    return html.Div(
        [
            html.Div(
                [
                    html.Strong(brand.get("brand_name", ""), className="me-2"),
                    html.Span(brand.get("industry") or "General", className="brand-card-industry"),
                ],
                className="mb-1",
            ),
            html.P(brand.get("brand_description") or "No description.", className="text-muted small mb-1"),
            html.Small(f"Tone: {brand.get('brand_tone') or '—'}  ·  Audience: {brand.get('target_audience') or '—'}"),
        ],
        className="brand-preview-box",
    )


def review_summary_row(label: str, value: str) -> html.Div:
    return html.Div(
        [
            html.Span(label, className="review-label"),
            html.Span(value or "—", className="review-value"),
        ],
        className="review-row",
    )
