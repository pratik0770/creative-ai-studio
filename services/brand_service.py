from __future__ import annotations

from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from database.connection import get_session
from database.models import Brand, User
from cloud.logging_config import get_logger

log = get_logger(__name__)


def _ensure_user(db: Session, user_id: str, email: str) -> User:
    """Upsert a user row (Firebase UID → DB)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        from datetime import datetime
        user = User(id=user_id, email=email, last_login=datetime.utcnow())
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


# ── Brand CRUD ─────────────────────────────────────────────────────────────────

def get_brands(user_id: str, search: str = "", industry: str = "") -> list[dict]:
    db = get_session()
    try:
        q = db.query(Brand).filter(Brand.user_id == user_id)
        if search:
            like = f"%{search}%"
            q = q.filter(
                or_(
                    Brand.brand_name.ilike(like),
                    Brand.brand_description.ilike(like),
                    Brand.industry.ilike(like),
                )
            )
        if industry:
            q = q.filter(Brand.industry == industry)
        q = q.order_by(Brand.created_at.desc())
        return [_brand_to_dict(b) for b in q.all()]
    finally:
        db.close()


def get_brand(brand_id: str, user_id: str) -> Optional[dict]:
    db = get_session()
    try:
        b = db.query(Brand).filter(Brand.id == brand_id, Brand.user_id == user_id).first()
        return _brand_to_dict(b) if b else None
    finally:
        db.close()


def create_brand(user_id: str, email: str, data: dict) -> tuple[bool, str, Optional[dict]]:
    """Returns (success, message, brand_dict)."""
    db = get_session()
    try:
        _ensure_user(db, user_id, email)
        # Uniqueness check
        existing = (
            db.query(Brand)
            .filter(Brand.user_id == user_id, Brand.brand_name == data["brand_name"].strip())
            .first()
        )
        if existing:
            return False, f"You already have a brand named \"{data['brand_name'].strip()}\".", None

        brand = Brand(
            user_id=user_id,
            brand_name=data["brand_name"].strip(),
            brand_tone=data.get("brand_tone", ""),
            brand_description=data.get("brand_description", ""),
            target_audience=data.get("target_audience", ""),
            brand_guidelines=data.get("brand_guidelines", ""),
            website=data.get("website", ""),
            industry=data.get("industry", ""),
        )
        db.add(brand)
        db.commit()
        db.refresh(brand)
        return True, "Brand created successfully.", _brand_to_dict(brand)
    except Exception as exc:
        db.rollback()
        log.error("create_brand error: %s", exc)
        return False, "An error occurred. Please try again.", None
    finally:
        db.close()


def update_brand(brand_id: str, user_id: str, data: dict) -> tuple[bool, str, Optional[dict]]:
    db = get_session()
    try:
        brand = db.query(Brand).filter(Brand.id == brand_id, Brand.user_id == user_id).first()
        if not brand:
            return False, "Brand not found.", None

        new_name = data.get("brand_name", brand.brand_name).strip()
        if new_name != brand.brand_name:
            conflict = (
                db.query(Brand)
                .filter(Brand.user_id == user_id, Brand.brand_name == new_name, Brand.id != brand_id)
                .first()
            )
            if conflict:
                return False, f"You already have a brand named \"{new_name}\".", None

        brand.brand_name = new_name
        brand.brand_tone = data.get("brand_tone", brand.brand_tone)
        brand.brand_description = data.get("brand_description", brand.brand_description)
        brand.target_audience = data.get("target_audience", brand.target_audience)
        brand.brand_guidelines = data.get("brand_guidelines", brand.brand_guidelines)
        brand.website = data.get("website", brand.website)
        brand.industry = data.get("industry", brand.industry)
        db.commit()
        db.refresh(brand)
        return True, "Brand updated successfully.", _brand_to_dict(brand)
    except Exception as exc:
        db.rollback()
        log.error("update_brand error: %s", exc)
        return False, "An error occurred. Please try again.", None
    finally:
        db.close()


def delete_brand(brand_id: str, user_id: str) -> tuple[bool, str]:
    db = get_session()
    try:
        brand = db.query(Brand).filter(Brand.id == brand_id, Brand.user_id == user_id).first()
        if not brand:
            return False, "Brand not found."
        db.delete(brand)
        db.commit()
        return True, "Brand deleted."
    except Exception as exc:
        db.rollback()
        log.error("delete_brand error: %s", exc)
        return False, "An error occurred. Please try again."
    finally:
        db.close()


def get_brand_stats(user_id: str) -> dict:
    db = get_session()
    try:
        total = db.query(Brand).filter(Brand.user_id == user_id).count()
        return {"total": total}
    finally:
        db.close()


def _brand_to_dict(b: Brand) -> dict:
    return {
        "id": b.id,
        "user_id": b.user_id,
        "brand_name": b.brand_name,
        "brand_tone": b.brand_tone or "",
        "brand_description": b.brand_description or "",
        "target_audience": b.target_audience or "",
        "brand_guidelines": b.brand_guidelines or "",
        "website": b.website or "",
        "industry": b.industry or "",
        "logo_url": b.logo_url or "",
        "created_at": b.created_at.isoformat() if b.created_at else "",
        "updated_at": b.updated_at.isoformat() if b.updated_at else "",
        "campaign_count": len(b.campaigns) if b.campaigns else 0,
    }
