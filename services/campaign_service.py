from __future__ import annotations

from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from database.connection import get_session
from database.models import Brand, Campaign
from cloud.logging_config import get_logger

log = get_logger(__name__)


# ── Campaign CRUD ──────────────────────────────────────────────────────────────

def get_campaigns(user_id: str, brand_id: str = "", status: str = "", search: str = "") -> list[dict]:
    db = get_session()
    try:
        q = (
            db.query(Campaign)
            .join(Brand, Campaign.brand_id == Brand.id)
            .filter(Brand.user_id == user_id)
        )
        if brand_id:
            q = q.filter(Campaign.brand_id == brand_id)
        if status:
            q = q.filter(Campaign.status == status)
        if search:
            like = f"%{search}%"
            q = q.filter(
                or_(
                    Campaign.campaign_name.ilike(like),
                    Campaign.campaign_description.ilike(like),
                    Campaign.campaign_theme.ilike(like),
                )
            )
        q = q.order_by(Campaign.created_at.desc())
        return [_campaign_to_dict(c) for c in q.all()]
    finally:
        db.close()


def get_campaign(campaign_id: str, user_id: str) -> Optional[dict]:
    db = get_session()
    try:
        c = (
            db.query(Campaign)
            .join(Brand, Campaign.brand_id == Brand.id)
            .filter(Campaign.id == campaign_id, Brand.user_id == user_id)
            .first()
        )
        return _campaign_to_dict(c) if c else None
    finally:
        db.close()


def create_campaign(user_id: str, data: dict) -> tuple[bool, str, Optional[dict]]:
    """Returns (success, message, campaign_dict)."""
    db = get_session()
    try:
        # Verify brand belongs to user
        brand = db.query(Brand).filter(
            Brand.id == data.get("brand_id"), Brand.user_id == user_id
        ).first()
        if not brand:
            return False, "Invalid brand selected.", None

        campaign = Campaign(
            brand_id=brand.id,
            campaign_name=data["campaign_name"].strip(),
            campaign_description=data.get("campaign_description", ""),
            campaign_theme=data.get("campaign_theme", ""),
            campaign_objective=data.get("campaign_objective", ""),
            target_audience=data.get("target_audience", ""),
            keywords=data.get("keywords", ""),
            content_pillars=data.get("content_pillars", ""),
            status=data.get("status", "draft"),
        )
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        return True, "Campaign created successfully.", _campaign_to_dict(campaign)
    except Exception as exc:
        db.rollback()
        log.error("create_campaign error: %s", exc)
        return False, "An error occurred. Please try again.", None
    finally:
        db.close()


def update_campaign(campaign_id: str, user_id: str, data: dict) -> tuple[bool, str, Optional[dict]]:
    db = get_session()
    try:
        c = (
            db.query(Campaign)
            .join(Brand, Campaign.brand_id == Brand.id)
            .filter(Campaign.id == campaign_id, Brand.user_id == user_id)
            .first()
        )
        if not c:
            return False, "Campaign not found.", None

        c.campaign_name = data.get("campaign_name", c.campaign_name).strip()
        c.campaign_description = data.get("campaign_description", c.campaign_description)
        c.campaign_theme = data.get("campaign_theme", c.campaign_theme)
        c.campaign_objective = data.get("campaign_objective", c.campaign_objective)
        c.target_audience = data.get("target_audience", c.target_audience)
        c.keywords = data.get("keywords", c.keywords)
        c.content_pillars = data.get("content_pillars", c.content_pillars)
        c.status = data.get("status", c.status)
        db.commit()
        db.refresh(c)
        return True, "Campaign updated successfully.", _campaign_to_dict(c)
    except Exception as exc:
        db.rollback()
        log.error("update_campaign error: %s", exc)
        return False, "An error occurred. Please try again.", None
    finally:
        db.close()


def delete_campaign(campaign_id: str, user_id: str) -> tuple[bool, str]:
    db = get_session()
    try:
        c = (
            db.query(Campaign)
            .join(Brand, Campaign.brand_id == Brand.id)
            .filter(Campaign.id == campaign_id, Brand.user_id == user_id)
            .first()
        )
        if not c:
            return False, "Campaign not found."
        db.delete(c)
        db.commit()
        return True, "Campaign deleted."
    except Exception as exc:
        db.rollback()
        log.error("delete_campaign error: %s", exc)
        return False, "An error occurred. Please try again."
    finally:
        db.close()


def get_campaign_stats(user_id: str) -> dict:
    db = get_session()
    try:
        q = (
            db.query(Campaign)
            .join(Brand, Campaign.brand_id == Brand.id)
            .filter(Brand.user_id == user_id)
        )
        total = q.count()
        active = q.filter(Campaign.status == "active").count()
        draft = total - active
        return {"total": total, "active": active, "draft": draft}
    finally:
        db.close()


def _campaign_to_dict(c: Campaign) -> dict:
    return {
        "id": c.id,
        "brand_id": c.brand_id,
        "brand_name": c.brand.brand_name if c.brand else "",
        "campaign_name": c.campaign_name,
        "campaign_description": c.campaign_description or "",
        "campaign_theme": c.campaign_theme or "",
        "campaign_objective": c.campaign_objective or "",
        "target_audience": c.target_audience or "",
        "keywords": c.keywords or "",
        "content_pillars": c.content_pillars or "",
        "status": c.status,
        "created_at": c.created_at.isoformat() if c.created_at else "",
        "updated_at": c.updated_at.isoformat() if c.updated_at else "",
    }
