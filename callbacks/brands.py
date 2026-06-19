"""Brand management callbacks — CRUD, search, filter, audience tags, colour swatches."""

from dash import Input, Output, State, callback, no_update, ctx, ALL
from dash import html
import dash_bootstrap_components as dbc
from flask import session as flask_session

from services.brand_service import (
    get_brands, get_brand, create_brand, update_brand, delete_brand,
)
from pages.brands import brand_card
from components.common import alert_success, alert_error, empty_state
from cloud.logging_config import get_logger

log = get_logger(__name__)


# ── Tag rendering helpers ──────────────────────────────────────────────────────

def _audience_tags(items: list, form_prefix: str) -> list:
    return [
        dbc.Badge(
            [
                item, " ",
                html.Span(
                    "×",
                    id={"type": "rm-audience", "form": form_prefix, "index": i},
                    style={"cursor": "pointer", "fontWeight": "bold"},
                    n_clicks=0,
                ),
            ],
            color="secondary",
            className="audience-tag me-1 mb-1",
        )
        for i, item in enumerate(items)
    ]


def _colour_swatches(colours: list, form_prefix: str) -> list:
    return [
        html.Div(
            [
                html.Div(
                    style={
                        "background": c,
                        "width": "24px",
                        "height": "24px",
                        "borderRadius": "4px",
                        "border": "1px solid rgba(255,255,255,0.15)",
                        "display": "inline-block",
                        "flexShrink": "0",
                    }
                ),
                html.Span(c, className="ms-1 small text-muted"),
                html.Span(
                    "×",
                    id={"type": "rm-colour", "form": form_prefix, "index": i},
                    className="ms-2",
                    style={"cursor": "pointer", "fontWeight": "bold", "opacity": "0.6"},
                    n_clicks=0,
                ),
            ],
            className="colour-swatch-item d-inline-flex align-items-center me-2 mb-1",
        )
        for i, c in enumerate(colours)
    ]


def register_brand_callbacks(app):

    # ── Load brands (search / filter / reload trigger) ─────────────────────────
    @app.callback(
        Output("brands-store", "data"),
        Output("brands-grid", "children"),
        Input("url", "pathname"),
        Input("brand-search", "value"),
        Input("brand-filter-industry", "value"),
        Input("brands-reload-trigger", "data"),
        prevent_initial_call=False,
    )
    def load_brands(pathname, search, industry, _trigger):
        if pathname != "/brands":
            return no_update, no_update
        uid = flask_session.get("user_id")
        if not uid:
            return [], []
        brands = get_brands(uid, search=search or "", industry=industry or "")
        if not brands:
            return [], empty_state(
                "bi-bookmark-star",
                "No brands yet",
                "Create your first brand to start building campaigns.",
                html.A(
                    [html.I(className="bi bi-plus-lg me-1"), "Create Brand"],
                    href="#",
                    id="empty-brand-create-link",
                    className="btn btn-primary btn-primary-custom mt-2",
                ),
            )
        cards = [
            dbc.Col(brand_card(b), xs=12, sm=6, lg=4, xl=3, className="mb-3")
            for b in brands
        ]
        return brands, dbc.Row(cards)

    # ── Empty-state "Create Brand" link → open modal ──────────────────────────
    @app.callback(
        Output("create-brand-modal", "is_open", allow_duplicate=True),
        Input("empty-brand-create-link", "n_clicks"),
        prevent_initial_call=True,
    )
    def open_modal_from_empty_state(n_clicks):
        if n_clicks:
            return True
        return no_update

    # ── Open create modal ──────────────────────────────────────────────────────
    @app.callback(
        Output("create-brand-modal", "is_open"),
        Output("create-brand-name", "value"),
        Output("create-brand-industry", "value"),
        Output("create-brand-tone", "value"),
        Output("create-brand-description", "value"),
        Output("create-brand-guidelines", "value"),
        Output("create-brand-website", "value"),
        Output("create-brand-audience-list", "data"),
        Output("create-brand-audience-display", "children"),
        Output("create-brand-colours-list", "data"),
        Output("create-brand-colours-display", "children"),
        Input("open-create-brand-modal", "n_clicks"),
        Input("close-create-brand-modal", "n_clicks"),
        State("create-brand-modal", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_create_modal(open_clicks, close_clicks, is_open):
        if ctx.triggered_id == "open-create-brand-modal":
            return True, "", None, "", "", "", "", [], [], [], []
        return (
            False,
            no_update, no_update, no_update, no_update, no_update, no_update,
            no_update, no_update, no_update, no_update,
        )

    # ── Save new brand ─────────────────────────────────────────────────────────
    @app.callback(
        Output("create-brand-alert", "children"),
        Output("create-brand-alert", "color"),
        Output("create-brand-alert", "is_open"),
        Output("create-brand-modal", "is_open", allow_duplicate=True),
        Output("brands-reload-trigger", "data", allow_duplicate=True),
        Output("brands-alert", "children"),
        Input("save-create-brand", "n_clicks"),
        State("create-brand-name", "value"),
        State("create-brand-industry", "value"),
        State("create-brand-tone", "value"),
        State("create-brand-description", "value"),
        State("create-brand-audience-list", "data"),
        State("create-brand-guidelines", "value"),
        State("create-brand-website", "value"),
        State("create-brand-colours-list", "data"),
        State("brands-reload-trigger", "data"),
        prevent_initial_call=True,
    )
    def save_new_brand(n_clicks, name, industry, tone, description, audience_list,
                       guidelines, website, colours_list, trigger):
        if not n_clicks:
            return no_update, no_update, no_update, no_update, no_update, no_update
        if not name or not name.strip():
            return "Brand Name is required.", "warning", True, True, no_update, no_update

        uid = flask_session.get("user_id")
        email = flask_session.get("user_email", "")
        ok, msg, brand = create_brand(uid, email, {
            "brand_name": name,
            "industry": industry or "",
            "brand_tone": tone or "",
            "brand_description": description or "",
            "target_audience": "\n".join(audience_list or []),
            "brand_guidelines": guidelines or "",
            "website": website or "",
            "brand_colours": colours_list or [],
        })
        if ok:
            return no_update, no_update, False, False, (trigger or 0) + 1, alert_success(msg)
        return msg, "danger", True, True, no_update, no_update

    # ── Open edit modal ────────────────────────────────────────────────────────
    @app.callback(
        Output("edit-brand-modal", "is_open"),
        Output("brand-edit-id", "data"),
        Output("edit-brand-name", "value"),
        Output("edit-brand-industry", "value"),
        Output("edit-brand-tone", "value"),
        Output("edit-brand-description", "value"),
        Output("edit-brand-guidelines", "value"),
        Output("edit-brand-website", "value"),
        Output("edit-brand-audience-list", "data"),
        Output("edit-brand-audience-display", "children"),
        Output("edit-brand-colours-list", "data"),
        Output("edit-brand-colours-display", "children"),
        Input({"type": "edit-brand-btn", "index": ALL}, "n_clicks"),
        Input("close-edit-brand-modal", "n_clicks"),
        State("brands-store", "data"),
        prevent_initial_call=True,
    )
    def open_edit_modal(edit_clicks, close_clicks, brands_data):
        triggered = ctx.triggered_id
        _no = no_update
        if triggered == "close-edit-brand-modal":
            return (False, _no, _no, _no, _no, _no, _no, _no, _no, _no, _no, _no)

        # Guard: pattern-matching fires with n_clicks=0 when brand cards load dynamically
        if not any(n for n in (edit_clicks or [])):
            return (_no, _no, _no, _no, _no, _no, _no, _no, _no, _no, _no, _no)

        if isinstance(triggered, dict) and triggered.get("type") == "edit-brand-btn":
            brand_id = triggered["index"]
            brand = next((b for b in (brands_data or []) if b["id"] == brand_id), None)
            if brand:
                audience_items = [
                    a for a in brand.get("target_audience", "").split("\n") if a.strip()
                ]
                colour_items = brand.get("brand_colours", []) or []
                return (
                    True,
                    brand_id,
                    brand.get("brand_name", ""),
                    brand.get("industry", ""),
                    brand.get("brand_tone", ""),
                    brand.get("brand_description", ""),
                    brand.get("brand_guidelines", ""),
                    brand.get("website", ""),
                    audience_items,
                    _audience_tags(audience_items, "edit-brand"),
                    colour_items,
                    _colour_swatches(colour_items, "edit-brand"),
                )
        return (_no, _no, _no, _no, _no, _no, _no, _no, _no, _no, _no, _no)

    # ── Save edit ──────────────────────────────────────────────────────────────
    @app.callback(
        Output("edit-brand-alert", "children"),
        Output("edit-brand-alert", "color"),
        Output("edit-brand-alert", "is_open"),
        Output("edit-brand-modal", "is_open", allow_duplicate=True),
        Output("brands-reload-trigger", "data", allow_duplicate=True),
        Output("brands-alert", "children", allow_duplicate=True),
        Input("save-edit-brand", "n_clicks"),
        State("brand-edit-id", "data"),
        State("edit-brand-name", "value"),
        State("edit-brand-industry", "value"),
        State("edit-brand-tone", "value"),
        State("edit-brand-description", "value"),
        State("edit-brand-audience-list", "data"),
        State("edit-brand-guidelines", "value"),
        State("edit-brand-website", "value"),
        State("edit-brand-colours-list", "data"),
        State("brands-reload-trigger", "data"),
        prevent_initial_call=True,
    )
    def save_edit_brand(n_clicks, brand_id, name, industry, tone, description,
                        audience_list, guidelines, website, colours_list, trigger):
        if not n_clicks or not brand_id:
            return no_update, no_update, no_update, no_update, no_update, no_update
        if not name or not name.strip():
            return "Brand Name is required.", "warning", True, True, no_update, no_update

        uid = flask_session.get("user_id")
        ok, msg, brand = update_brand(brand_id, uid, {
            "brand_name": name,
            "industry": industry or "",
            "brand_tone": tone or "",
            "brand_description": description or "",
            "target_audience": "\n".join(audience_list or []),
            "brand_guidelines": guidelines or "",
            "website": website or "",
            "brand_colours": colours_list or [],
        })
        if ok:
            return no_update, no_update, False, False, (trigger or 0) + 1, alert_success(msg)
        return msg, "danger", True, True, no_update, no_update

    # ── Open delete confirm ────────────────────────────────────────────────────
    @app.callback(
        Output("delete-brand-modal", "is_open"),
        Output("brand-delete-id", "data"),
        Input({"type": "delete-brand-btn", "index": ALL}, "n_clicks"),
        Input("cancel-delete-brand", "n_clicks"),
        Input("confirm-delete-brand", "n_clicks"),
        prevent_initial_call=True,
    )
    def handle_delete_modal(delete_clicks, cancel_clicks, confirm_clicks):
        triggered = ctx.triggered_id
        if triggered == "cancel-delete-brand" or triggered == "confirm-delete-brand":
            return False, None
        # Guard: fires with n_clicks=0 when brand cards are dynamically added
        if not any(n for n in (delete_clicks or [])):
            return no_update, no_update
        if isinstance(triggered, dict) and triggered.get("type") == "delete-brand-btn":
            return True, triggered["index"]
        return no_update, no_update

    # ── Confirm delete ─────────────────────────────────────────────────────────
    @app.callback(
        Output("brands-reload-trigger", "data", allow_duplicate=True),
        Output("brands-alert", "children", allow_duplicate=True),
        Output("delete-brand-modal", "is_open", allow_duplicate=True),
        Input("confirm-delete-brand", "n_clicks"),
        State("brand-delete-id", "data"),
        State("brands-reload-trigger", "data"),
        prevent_initial_call=True,
    )
    def confirm_delete_brand(n_clicks, brand_id, trigger):
        if not n_clicks or not brand_id:
            return no_update, no_update, no_update
        uid = flask_session.get("user_id")
        ok, msg = delete_brand(brand_id, uid)
        if ok:
            return (trigger or 0) + 1, alert_success(msg), False
        return no_update, alert_error(msg), False

    # ── Tone suggestion chips ──────────────────────────────────────────────────
    @app.callback(
        Output("create-brand-tone", "value", allow_duplicate=True),
        Input({"type": "tone-suggestion", "form": "create-brand", "tone": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def set_create_tone_from_chip(n_clicks_list):
        triggered = ctx.triggered_id
        if isinstance(triggered, dict) and triggered.get("type") == "tone-suggestion":
            return triggered["tone"]
        return no_update

    @app.callback(
        Output("edit-brand-tone", "value", allow_duplicate=True),
        Input({"type": "tone-suggestion", "form": "edit-brand", "tone": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def set_edit_tone_from_chip(n_clicks_list):
        triggered = ctx.triggered_id
        if isinstance(triggered, dict) and triggered.get("type") == "tone-suggestion":
            return triggered["tone"]
        return no_update

    # ── Audience tag management — Create form ──────────────────────────────────
    @app.callback(
        Output("create-brand-audience-list", "data", allow_duplicate=True),
        Output("create-brand-audience-display", "children", allow_duplicate=True),
        Output("create-brand-audience-input", "value"),
        Input("create-brand-audience-add", "n_clicks"),
        Input({"type": "rm-audience", "form": "create-brand", "index": ALL}, "n_clicks"),
        State("create-brand-audience-input", "value"),
        State("create-brand-audience-list", "data"),
        prevent_initial_call=True,
    )
    def manage_create_audience(add_clicks, rm_clicks, text, current_list):
        items = list(current_list or [])
        triggered = ctx.triggered_id

        if triggered == "create-brand-audience-add":
            if text and text.strip() and text.strip() not in items:
                items.append(text.strip())
            return items, _audience_tags(items, "create-brand"), ""

        if isinstance(triggered, dict) and triggered.get("type") == "rm-audience":
            if not any(n for n in (rm_clicks or [])):
                return no_update, no_update, no_update
            idx = triggered["index"]
            if 0 <= idx < len(items):
                items.pop(idx)
            return items, _audience_tags(items, "create-brand"), no_update

        return no_update, no_update, no_update

    # ── Audience tag management — Edit form ────────────────────────────────────
    @app.callback(
        Output("edit-brand-audience-list", "data", allow_duplicate=True),
        Output("edit-brand-audience-display", "children", allow_duplicate=True),
        Output("edit-brand-audience-input", "value"),
        Input("edit-brand-audience-add", "n_clicks"),
        Input({"type": "rm-audience", "form": "edit-brand", "index": ALL}, "n_clicks"),
        State("edit-brand-audience-input", "value"),
        State("edit-brand-audience-list", "data"),
        prevent_initial_call=True,
    )
    def manage_edit_audience(add_clicks, rm_clicks, text, current_list):
        items = list(current_list or [])
        triggered = ctx.triggered_id

        if triggered == "edit-brand-audience-add":
            if text and text.strip() and text.strip() not in items:
                items.append(text.strip())
            return items, _audience_tags(items, "edit-brand"), ""

        if isinstance(triggered, dict) and triggered.get("type") == "rm-audience":
            if not any(n for n in (rm_clicks or [])):
                return no_update, no_update, no_update
            idx = triggered["index"]
            if 0 <= idx < len(items):
                items.pop(idx)
            return items, _audience_tags(items, "edit-brand"), no_update

        return no_update, no_update, no_update

    # ── Colour swatch management — Create form ─────────────────────────────────
    @app.callback(
        Output("create-brand-colours-list", "data", allow_duplicate=True),
        Output("create-brand-colours-display", "children", allow_duplicate=True),
        Input("create-brand-colour-add", "n_clicks"),
        Input({"type": "rm-colour", "form": "create-brand", "index": ALL}, "n_clicks"),
        State("create-brand-colour-picker", "value"),
        State("create-brand-colours-list", "data"),
        prevent_initial_call=True,
    )
    def manage_create_colours(add_clicks, rm_clicks, hex_val, current_list):
        colours = list(current_list or [])
        triggered = ctx.triggered_id

        if triggered == "create-brand-colour-add":
            if hex_val and hex_val.strip() and hex_val.strip() not in colours:
                colours.append(hex_val.strip())
            return colours, _colour_swatches(colours, "create-brand")

        if isinstance(triggered, dict) and triggered.get("type") == "rm-colour":
            if not any(n for n in (rm_clicks or [])):
                return no_update, no_update
            idx = triggered["index"]
            if 0 <= idx < len(colours):
                colours.pop(idx)
            return colours, _colour_swatches(colours, "create-brand")

        return no_update, no_update

    # ── Colour swatch management — Edit form ───────────────────────────────────
    @app.callback(
        Output("edit-brand-colours-list", "data", allow_duplicate=True),
        Output("edit-brand-colours-display", "children", allow_duplicate=True),
        Input("edit-brand-colour-add", "n_clicks"),
        Input({"type": "rm-colour", "form": "edit-brand", "index": ALL}, "n_clicks"),
        State("edit-brand-colour-picker", "value"),
        State("edit-brand-colours-list", "data"),
        prevent_initial_call=True,
    )
    def manage_edit_colours(add_clicks, rm_clicks, hex_val, current_list):
        colours = list(current_list or [])
        triggered = ctx.triggered_id

        if triggered == "edit-brand-colour-add":
            if hex_val and hex_val.strip() and hex_val.strip() not in colours:
                colours.append(hex_val.strip())
            return colours, _colour_swatches(colours, "edit-brand")

        if isinstance(triggered, dict) and triggered.get("type") == "rm-colour":
            if not any(n for n in (rm_clicks or [])):
                return no_update, no_update
            idx = triggered["index"]
            if 0 <= idx < len(colours):
                colours.pop(idx)
            return colours, _colour_swatches(colours, "edit-brand")

        return no_update, no_update
