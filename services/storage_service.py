"""Google Cloud Storage service for brand/campaign assets."""

from __future__ import annotations

import os
from typing import Optional

from config.settings import settings
from cloud.logging_config import get_logger

log = get_logger(__name__)

_gcs_client = None


def _get_client():
    global _gcs_client
    if _gcs_client is None:
        try:
            from google.cloud import storage
            _gcs_client = storage.Client(project=settings.GCP_PROJECT_ID)
        except Exception as exc:
            log.warning("GCS client init failed (GCS disabled): %s", exc)
    return _gcs_client


def upload_file(
    file_bytes: bytes,
    destination_blob: str,
    content_type: str = "application/octet-stream",
) -> Optional[str]:
    """Upload bytes to GCS and return the public URL."""
    client = _get_client()
    if not client or not settings.GCS_BUCKET:
        log.warning("GCS not configured — skipping upload.")
        return None
    try:
        bucket = client.bucket(settings.GCS_BUCKET)
        blob = bucket.blob(destination_blob)
        blob.upload_from_string(file_bytes, content_type=content_type)
        return f"https://storage.googleapis.com/{settings.GCS_BUCKET}/{destination_blob}"
    except Exception as exc:
        log.error("GCS upload error: %s", exc)
        return None


def delete_file(blob_name: str) -> bool:
    client = _get_client()
    if not client or not settings.GCS_BUCKET:
        return False
    try:
        bucket = client.bucket(settings.GCS_BUCKET)
        bucket.blob(blob_name).delete()
        return True
    except Exception as exc:
        log.error("GCS delete error: %s", exc)
        return False


def get_signed_url(blob_name: str, expiration_seconds: int = 3600) -> Optional[str]:
    """Generate a signed URL for temporary access."""
    client = _get_client()
    if not client or not settings.GCS_BUCKET:
        return None
    try:
        import datetime
        bucket = client.bucket(settings.GCS_BUCKET)
        blob = bucket.blob(blob_name)
        url = blob.generate_signed_url(
            expiration=datetime.timedelta(seconds=expiration_seconds),
            method="GET",
        )
        return url
    except Exception as exc:
        log.error("GCS signed URL error: %s", exc)
        return None


def brand_asset_path(user_id: str, brand_id: str, filename: str) -> str:
    return f"brands/{user_id}/{brand_id}/{filename}"


def campaign_asset_path(user_id: str, campaign_id: str, filename: str) -> str:
    return f"campaigns/{user_id}/{campaign_id}/{filename}"
