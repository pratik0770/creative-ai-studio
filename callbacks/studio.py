"""Campaign Studio callbacks — 3-step guided workflow."""

from dash import Input, Output, State, no_update, ctx
from dash import html
import dash_bootstrap_components as dbc
from flask import session as flask_session

from services.brand_service import get_brands, create_brand, get_brand
from services.campaign_service import create_campaign
from components.common import alert_error, alert_success, step_indicator
from pages.studio import brand_preview_card, review_summary_row
from cloud.logging_config import get_logger

log = get_logger(__name__)


def register_studio_callbacks(app):

    # ── Load brands on page entry ──────────────────────────────────────────────
    @app.callback(
        Output("studio-brands-list", "data"),
        Output("studio-brand-select", "options"),
        Input("url", "pathname"),
        prevent_initial_call=False,
    )
    def load_studio_brands(pathname):
        if pathname != "/studio":
            return no_update, no_update
        uid = flask_session.get("user_id")
        if not uid:
            return [], []
        brands = get_brands(uid)
        opts = [{"label": b["brand_name"], "value": b["id"]} for b in brands]
        return brands, opts

    # ── Toggle select vs create brand section ──────────────────────────────────
    @app.callback(
        Output("studio-select-brand-section", "style"),
        Output("studio-create-brand-section", "style"),
        Input("studio-brand-mode", "value"),
    )
    def toggle_brand_mode(mode):
        if mode == "create":
            return {"display": "none"}, {"display": "block"}
        return {"display": "block"}, {"display": "none"}

    # ── Brand preview on selection ─────────────────────────────────────────────
    @app.callback(
        Output("studio-brand-preview", "children"),
        Input("studio-brand-select", "value"),
        State("studio-brands-list", "data"),
    )
    def show_brand_preview(brand_id, brands):
        if not brand_id or not brands:
            return html.P("Select a brand above to preview its details.", className="text-muted small")
        brand = next((b for b in brands if b["id"] == brand_id), None)
        if brand:
            return brand_preview_card(brand)
        return no_update

    # ── Step 1 → Step 2 ───────────────────────────────────────────────────────
    @app.callback(
        Output("studio-step", "data"),
        Output("studio-brand-data", "data"),
        Output("studio-alert", "children"),
        Output("studio-create-brand-alert", "children"),
        Output("studio-create-brand-alert", "color"),
        Output("studio-create-brand-alert", "is_open"),
        Input("studio-step1-next", "n_clicks"),
        State("studio-brand-mode", "value"),
        State("studio-brand-select", "value"),
        State("studio-brands-list", "data"),
        # New brand fields
        State("studio-new-brand-name", "value"),
        State("studio-new-brand-industry", "value"),
        State("studio-new-brand-tone", "value"),
        State("studio-new-brand-description", "value"),
        State("studio-new-brand-audience", "value"),
        State("studio-new-brand-guidelines", "value"),
        State("studio-new-brand-website", "value"),
        prevent_initial_call=True,
    )
    def step1_next(
        n_clicks, mode, brand_id, brands_list,
        new_name, new_industry, new_tone, new_desc, new_audience, new_guidelines, new_website,
    ):
        if not n_clicks:
            return no_update, no_update, no_update, no_update, no_update, no_update

        uid = flask_session.get("user_id")
        email = flask_session.get("user_email", "")

        if mode == "select":
            if not brand_id:
                return no_update, no_update, alert_error("Please select a brand."), no_update, no_update, no_update
            brand = next((b for b in (brands_list or []) if b["id"] == brand_id), None)
            if not brand:
                return no_update, no_update, alert_error("Brand not found."), no_update, no_update, no_update
            return 2, brand, None, no_update, no_update, no_update

        else:  # create
            if not new_name or not new_name.strip():
                return no_update, no_update, no_update, "Brand Name is required.", "warning", True

            ok, msg, brand = create_brand(uid, email, {
                "brand_name": new_name,
                "industry": new_industry or "",
                "brand_tone": new_tone or "",
                "brand_description": new_desc or "",
                "target_audience": new_audience or "",
                "brand_guidelines": new_guidelines or "",
                "website": new_website or "",
            })
            if not ok:
                return no_update, no_update, no_update, msg, "danger", True
            return 2, brand, None, no_update, no_update, no_update

    # ── Step 2 → Step 3 ───────────────────────────────────────────────────────
    @app.callback(
        Output("studio-step", "data", allow_duplicate=True),
        Output("studio-campaign-data", "data"),
        Output("studio-alert", "children", allow_duplicate=True),
        Input("studio-step2-next", "n_clicks"),
        State("studio-campaign-name", "value"),
        State("studio-campaign-objective", "value"),
        State("studio-campaign-theme", "value"),
        State("studio-campaign-description", "value"),
        State("studio-campaign-audience", "value"),
        State("studio-campaign-keywords", "value"),
        State("studio-campaign-pillars", "value"),
        State("studio-campaign-status", "value"),
        prevent_initial_call=True,
    )
    def step2_next(n_clicks, name, objective, theme, description, audience, keywords, pillars, status):
        if not n_clicks:
            return no_update, no_update, no_update
        if not name or not name.strip():
            return no_update, no_update, alert_error("Campaign Name is required.")
        campaign_data = {
            "campaign_name": name.strip(),
            "campaign_objective": objective or "",
            "campaign_theme": theme or "",
            "campaign_description": description or "",
            "target_audience": audience or "",
            "keywords": keywords or "",
            "content_pillars": pillars or "",
            "status": status or "draft",
        }
        return 3, campaign_data, None

    # ── Step 2 ← Step 1 ───────────────────────────────────────────────────────
    @app.callback(
        Output("studio-step", "data", allow_duplicate=True),
        Output("studio-alert", "children", allow_duplicate=True),
        Input("studio-step2-back", "n_clicks"),
        prevent_initial_call=True,
    )
    def step2_back(n_clicks):
        if n_clicks:
            return 1, None
        return no_update, no_update

    # ── Step 3 ← Step 2 ───────────────────────────────────────────────────────
    @app.callback(
        Output("studio-step", "data", allow_duplicate=True),
        Output("studio-alert", "children", allow_duplicate=True),
        Input("studio-step3-back", "n_clicks"),
        prevent_initial_call=True,
    )
    def step3_back(n_clicks):
        if n_clicks:
            return 2, None
        return no_update, no_update

    # ── Render step visibility + step indicator ────────────────────────────────
    @app.callback(
        Output("studio-step-indicator", "children"),
        Output("studio-step-1", "style"),
        Output("studio-step-2", "style"),
        Output("studio-step-3", "style"),
        Input("studio-step", "data"),
    )
    def render_step(step):
        step = step or 1
        show = {"display": "block"}
        hide = {"display": "none"}
        indicator = step_indicator(["Select Brand", "Campaign Setup", "Review & Create"], step)
        return (
            indicator,
            show if step == 1 else hide,
            show if step == 2 else hide,
            show if step == 3 else hide,
        )

    # ── Render review summaries ────────────────────────────────────────────────
    @app.callback(
        Output("studio-review-brand", "children"),
        Output("studio-review-campaign", "children"),
        Input("studio-step", "data"),
        State("studio-brand-data", "data"),
        State("studio-campaign-data", "data"),
    )
    def render_review(step, brand_data, campaign_data):
        if step != 3:
            return no_update, no_update
        b = brand_data or {}
        c = campaign_data or {}
        brand_summary = html.Div([
            review_summary_row("Brand Name", b.get("brand_name")),
            review_summary_row("Industry", b.get("industry")),
            review_summary_row("Tone", b.get("brand_tone")),
            review_summary_row("Target Audience", b.get("target_audience")),
            review_summary_row("Website", b.get("website")),
        ])
        campaign_summary = html.Div([
            review_summary_row("Campaign Name", c.get("campaign_name")),
            review_summary_row("Objective", c.get("campaign_objective")),
            review_summary_row("Theme", c.get("campaign_theme")),
            review_summary_row("Status", (c.get("status") or "draft").capitalize()),
            review_summary_row("Keywords", c.get("keywords")),
            review_summary_row("Content Pillars", c.get("content_pillars")),
        ])
        return brand_summary, campaign_summary

    # ── Create Campaign (final) ────────────────────────────────────────────────
    @app.callback(
        Output("studio-alert", "children", allow_duplicate=True),
        Output("studio-step", "data", allow_duplicate=True),
        Output("url", "pathname", allow_duplicate=True),
        Input("studio-create-campaign", "n_clicks"),
        Input("studio-save-draft", "n_clicks"),
        State("studio-brand-data", "data"),
        State("studio-campaign-data", "data"),
        prevent_initial_call=True,
    )
    def create_campaign_final(create_clicks, draft_clicks, brand_data, campaign_data):
        triggered = ctx.triggered_id
        if not triggered or (not create_clicks and not draft_clicks):
            return no_update, no_update, no_update

        uid = flask_session.get("user_id")
        b = brand_data or {}
        c = dict(campaign_data or {})
        c["brand_id"] = b.get("id")

        if triggered == "studio-save-draft":
            c["status"] = "draft"
        else:
            c["status"] = c.get("status", "active")

        ok, msg, _ = create_campaign(uid, c)
        if ok:
            return alert_success(f"Campaign '{c.get('campaign_name')}' created!"), 1, "/campaigns"
        return alert_error(msg), no_update, no_update
