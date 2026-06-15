"""Dashboard callbacks — stats and recent activity."""

from dash import Input, Output, no_update
from dash import html
import dash_bootstrap_components as dbc
from flask import session as flask_session

from services.brand_service import get_brand_stats
from services.campaign_service import get_campaign_stats, get_campaigns
from components.common import stat_card, badge_status, empty_state
from cloud.logging_config import get_logger

log = get_logger(__name__)


def register_dashboard_callbacks(app):

    @app.callback(
        Output("stat-brands", "children"),
        Output("stat-campaigns", "children"),
        Output("stat-active", "children"),
        Output("stat-drafts", "children"),
        Output("recent-campaigns-list", "children"),
        Input("url", "pathname"),
        Input("dashboard-refresh", "n_intervals"),
    )
    def update_dashboard(pathname, _intervals):
        if pathname not in ("/", ""):
            return no_update, no_update, no_update, no_update, no_update

        uid = flask_session.get("user_id")
        if not uid:
            return no_update, no_update, no_update, no_update, no_update

        brand_stats = get_brand_stats(uid)
        camp_stats = get_campaign_stats(uid)
        recent = get_campaigns(uid)[:5]

        brands_card = stat_card("Total Brands", brand_stats["total"], "bi-bookmark-star-fill", "primary")
        campaigns_card = stat_card("Total Campaigns", camp_stats["total"], "bi-megaphone-fill", "violet")
        active_card = stat_card("Active Campaigns", camp_stats["active"], "bi-lightning-charge-fill", "success")
        drafts_card = stat_card("Drafts", camp_stats["draft"], "bi-file-earmark-text-fill", "warning")

        if not recent:
            recent_content = empty_state(
                "bi-megaphone",
                "No campaigns yet",
                "Create your first campaign using the Campaign Studio.",
                dbc.Button(
                    [html.I(className="bi bi-magic me-1"), "Open Studio"],
                    href="/studio",
                    color="primary",
                    className="btn-primary-custom mt-2",
                ),
            )
        else:
            recent_content = html.Div([
                html.Div(
                    [
                        html.Div(
                            [
                                html.Strong(c["campaign_name"], className="d-block"),
                                html.Small(c.get("brand_name", ""), className="text-muted"),
                            ]
                        ),
                        badge_status(c["status"]),
                    ],
                    className="recent-campaign-row",
                )
                for c in recent
            ])

        return brands_card, campaigns_card, active_card, drafts_card, recent_content
