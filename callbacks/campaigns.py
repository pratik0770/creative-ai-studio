"""Campaign management callbacks — CRUD, search, filter."""

from dash import Input, Output, State, callback, no_update, ctx, ALL
from dash import html
import dash_bootstrap_components as dbc
from flask import session as flask_session

from services.campaign_service import (
    get_campaigns, get_campaign, create_campaign, update_campaign, delete_campaign,
)
from services.brand_service import get_brands
from pages.campaigns import campaign_row
from components.common import alert_success, alert_error, empty_state
from cloud.logging_config import get_logger

log = get_logger(__name__)


def register_campaign_callbacks(app):

    # ── Load campaigns ──────────────────────────────────────────────────────────
    @app.callback(
        Output("campaigns-store", "data"),
        Output("campaigns-list", "children"),
        Output("campaign-filter-brand", "options"),
        Output("campaign-brands-store", "data"),
        Input("url", "pathname"),
        Input("campaign-search", "value"),
        Input("campaign-filter-brand", "value"),
        Input("campaign-filter-status", "value"),
        Input("campaigns-reload-trigger", "data"),
        prevent_initial_call=False,
    )
    def load_campaigns(pathname, search, brand_id_filter, status_filter, _trigger):
        if pathname != "/campaigns":
            return no_update, no_update, no_update, no_update
        uid = flask_session.get("user_id")
        if not uid:
            return [], [], [], []

        # Load brands for filter dropdown
        brands = get_brands(uid)
        brand_opts = [{"label": "All Brands", "value": ""}] + [
            {"label": b["brand_name"], "value": b["id"]} for b in brands
        ]

        campaigns = get_campaigns(
            uid,
            brand_id=brand_id_filter or "",
            status=status_filter or "",
            search=search or "",
        )

        if not campaigns:
            return [], empty_state(
                "bi-megaphone",
                "No campaigns yet",
                "Create your first campaign using the Campaign Studio.",
                dbc.Button(
                    [html.I(className="bi bi-magic me-1"), "Open Studio"],
                    href="/studio",
                    color="primary",
                    className="btn-primary-custom mt-2",
                ),
            ), brand_opts, brands

        rows = html.Div([campaign_row(c) for c in campaigns], className="campaign-list-inner")
        return campaigns, rows, brand_opts, brands

    # ── Open create modal ──────────────────────────────────────────────────────
    @app.callback(
        Output("create-campaign-modal", "is_open"),
        Output("create-campaign-name", "value"),
        Output("create-campaign-brand", "value"),
        Output("create-campaign-objective", "value"),
        Output("create-campaign-theme", "value"),
        Output("create-campaign-description", "value"),
        Output("create-campaign-audience", "value"),
        Output("create-campaign-keywords", "value"),
        Output("create-campaign-pillars", "value"),
        Output("create-campaign-status", "value"),
        Output("create-campaign-brand", "options"),
        Input("open-create-campaign-modal", "n_clicks"),
        Input("close-create-campaign-modal", "n_clicks"),
        State("campaign-brands-store", "data"),
        prevent_initial_call=True,
    )
    def toggle_create_campaign_modal(open_clicks, close_clicks, brands):
        if ctx.triggered_id == "open-create-campaign-modal":
            opts = [{"label": b["brand_name"], "value": b["id"]} for b in (brands or [])]
            return True, "", None, None, "", "", "", "", "", "draft", opts
        return False, *([no_update] * 10)

    # ── Save new campaign ──────────────────────────────────────────────────────
    @app.callback(
        Output("create-campaign-alert", "children"),
        Output("create-campaign-alert", "color"),
        Output("create-campaign-alert", "is_open"),
        Output("create-campaign-modal", "is_open", allow_duplicate=True),
        Output("campaigns-reload-trigger", "data", allow_duplicate=True),
        Output("campaigns-alert", "children"),
        Input("save-create-campaign", "n_clicks"),
        State("create-campaign-name", "value"),
        State("create-campaign-brand", "value"),
        State("create-campaign-objective", "value"),
        State("create-campaign-theme", "value"),
        State("create-campaign-description", "value"),
        State("create-campaign-audience", "value"),
        State("create-campaign-keywords", "value"),
        State("create-campaign-pillars", "value"),
        State("create-campaign-status", "value"),
        State("campaigns-reload-trigger", "data"),
        prevent_initial_call=True,
    )
    def save_new_campaign(n_clicks, name, brand_id, objective, theme, description, audience, keywords, pillars, status, trigger):
        if not n_clicks:
            return no_update, no_update, no_update, no_update, no_update, no_update
        if not name or not name.strip():
            return "Campaign Name is required.", "warning", True, True, no_update, no_update
        if not brand_id:
            return "Please select a brand.", "warning", True, True, no_update, no_update

        uid = flask_session.get("user_id")
        ok, msg, campaign = create_campaign(uid, {
            "brand_id": brand_id,
            "campaign_name": name,
            "campaign_objective": objective or "",
            "campaign_theme": theme or "",
            "campaign_description": description or "",
            "target_audience": audience or "",
            "keywords": keywords or "",
            "content_pillars": pillars or "",
            "status": status or "draft",
        })
        if ok:
            return no_update, no_update, False, False, (trigger or 0) + 1, alert_success(msg)
        return msg, "danger", True, True, no_update, no_update

    # ── Open edit modal ────────────────────────────────────────────────────────
    @app.callback(
        Output("edit-campaign-modal", "is_open"),
        Output("campaign-edit-id", "data"),
        Output("edit-campaign-name", "value"),
        Output("edit-campaign-brand", "value"),
        Output("edit-campaign-objective", "value"),
        Output("edit-campaign-theme", "value"),
        Output("edit-campaign-description", "value"),
        Output("edit-campaign-audience", "value"),
        Output("edit-campaign-keywords", "value"),
        Output("edit-campaign-pillars", "value"),
        Output("edit-campaign-status", "value"),
        Output("edit-campaign-brand", "options"),
        Input({"type": "edit-campaign-btn", "index": ALL}, "n_clicks"),
        Input("close-edit-campaign-modal", "n_clicks"),
        State("campaigns-store", "data"),
        State("campaign-brands-store", "data"),
        prevent_initial_call=True,
    )
    def open_edit_campaign_modal(edit_clicks, close_clicks, campaigns_data, brands):
        triggered = ctx.triggered_id
        if triggered == "close-edit-campaign-modal":
            return False, *([no_update] * 11)

        if isinstance(triggered, dict) and triggered.get("type") == "edit-campaign-btn":
            camp_id = triggered["index"]
            c = next((x for x in (campaigns_data or []) if x["id"] == camp_id), None)
            opts = [{"label": b["brand_name"], "value": b["id"]} for b in (brands or [])]
            if c:
                return (
                    True, camp_id,
                    c.get("campaign_name", ""),
                    c.get("brand_id", ""),
                    c.get("campaign_objective", ""),
                    c.get("campaign_theme", ""),
                    c.get("campaign_description", ""),
                    c.get("target_audience", ""),
                    c.get("keywords", ""),
                    c.get("content_pillars", ""),
                    c.get("status", "draft"),
                    opts,
                )
        return no_update, *([no_update] * 11)

    # ── Save edit ──────────────────────────────────────────────────────────────
    @app.callback(
        Output("edit-campaign-alert", "children"),
        Output("edit-campaign-alert", "color"),
        Output("edit-campaign-alert", "is_open"),
        Output("edit-campaign-modal", "is_open", allow_duplicate=True),
        Output("campaigns-reload-trigger", "data", allow_duplicate=True),
        Output("campaigns-alert", "children", allow_duplicate=True),
        Input("save-edit-campaign", "n_clicks"),
        State("campaign-edit-id", "data"),
        State("edit-campaign-name", "value"),
        State("edit-campaign-brand", "value"),
        State("edit-campaign-objective", "value"),
        State("edit-campaign-theme", "value"),
        State("edit-campaign-description", "value"),
        State("edit-campaign-audience", "value"),
        State("edit-campaign-keywords", "value"),
        State("edit-campaign-pillars", "value"),
        State("edit-campaign-status", "value"),
        State("campaigns-reload-trigger", "data"),
        prevent_initial_call=True,
    )
    def save_edit_campaign(n_clicks, camp_id, name, brand_id, objective, theme, description, audience, keywords, pillars, status, trigger):
        if not n_clicks or not camp_id:
            return no_update, no_update, no_update, no_update, no_update, no_update
        if not name or not name.strip():
            return "Campaign Name is required.", "warning", True, True, no_update, no_update

        uid = flask_session.get("user_id")
        ok, msg, _ = update_campaign(camp_id, uid, {
            "campaign_name": name,
            "brand_id": brand_id,
            "campaign_objective": objective or "",
            "campaign_theme": theme or "",
            "campaign_description": description or "",
            "target_audience": audience or "",
            "keywords": keywords or "",
            "content_pillars": pillars or "",
            "status": status or "draft",
        })
        if ok:
            return no_update, no_update, False, False, (trigger or 0) + 1, alert_success(msg)
        return msg, "danger", True, True, no_update, no_update

    # ── Delete flow ────────────────────────────────────────────────────────────
    @app.callback(
        Output("delete-campaign-modal", "is_open"),
        Output("campaign-delete-id", "data"),
        Input({"type": "delete-campaign-btn", "index": ALL}, "n_clicks"),
        Input("cancel-delete-campaign", "n_clicks"),
        Input("confirm-delete-campaign", "n_clicks"),
        prevent_initial_call=True,
    )
    def handle_delete_campaign_modal(delete_clicks, cancel, confirm):
        triggered = ctx.triggered_id
        if triggered in ("cancel-delete-campaign", "confirm-delete-campaign"):
            return False, None
        if isinstance(triggered, dict) and triggered.get("type") == "delete-campaign-btn":
            return True, triggered["index"]
        return no_update, no_update

    @app.callback(
        Output("campaigns-reload-trigger", "data", allow_duplicate=True),
        Output("campaigns-alert", "children", allow_duplicate=True),
        Output("delete-campaign-modal", "is_open", allow_duplicate=True),
        Input("confirm-delete-campaign", "n_clicks"),
        State("campaign-delete-id", "data"),
        State("campaigns-reload-trigger", "data"),
        prevent_initial_call=True,
    )
    def confirm_delete_campaign(n_clicks, camp_id, trigger):
        if not n_clicks or not camp_id:
            return no_update, no_update, no_update
        uid = flask_session.get("user_id")
        ok, msg = delete_campaign(camp_id, uid)
        if ok:
            return (trigger or 0) + 1, alert_success(msg), False
        return no_update, alert_error(msg), False
