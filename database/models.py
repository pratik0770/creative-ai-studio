from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Text, DateTime, ForeignKey,
    Boolean, UniqueConstraint, func,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


def _uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String(128), primary_key=True)          # Firebase UID
    email = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))

    brands = relationship("Brand", back_populates="user", cascade="all, delete-orphan")


class Brand(Base):
    __tablename__ = "brands"

    id = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(String(128), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    brand_name = Column(String(255), nullable=False)
    brand_tone = Column(String(100))
    brand_description = Column(Text)
    target_audience = Column(Text)
    brand_guidelines = Column(Text)
    website = Column(String(500))
    industry = Column(String(100))
    brand_colours = Column(Text)                          # Comma-separated hex codes
    logo_url = Column(String(500))                       # GCS URL (future)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="brands")
    campaigns = relationship("Campaign", back_populates="brand", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("user_id", "brand_name", name="uq_brand_name_per_user"),
    )


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(String(36), primary_key=True, default=_uuid)
    brand_id = Column(String(36), ForeignKey("brands.id", ondelete="CASCADE"), nullable=False)
    campaign_name = Column(String(255), nullable=False)
    campaign_description = Column(Text)
    campaign_theme = Column(String(255))
    campaign_objective = Column(String(255))
    target_audience = Column(Text)
    keywords = Column(Text)                              # Comma-separated
    content_pillars = Column(Text)                       # Comma-separated
    status = Column(String(20), nullable=False, default="draft")  # draft | active
    gcs_assets_prefix = Column(String(500))              # GCS folder prefix
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    brand = relationship("Brand", back_populates="campaigns")
    generated_assets = relationship("GeneratedAsset", back_populates="campaign", cascade="all, delete-orphan")


class GeneratedAsset(Base):
    """Future: stores Vertex AI / Imagen generated content."""
    __tablename__ = "generated_assets"

    id = Column(String(36), primary_key=True, default=_uuid)
    campaign_id = Column(String(36), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    asset_type = Column(String(50))                      # image | text | video
    prompt = Column(Text)
    gcs_url = Column(String(500))
    model_used = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    campaign = relationship("Campaign", back_populates="generated_assets")
