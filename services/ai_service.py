"""Vertex AI / Imagen integration — production-ready stubs for future AI workflows."""

from __future__ import annotations

from typing import Optional

from config.settings import settings
from cloud.logging_config import get_logger

log = get_logger(__name__)

_vertex_initialised = False


def _init_vertex():
    global _vertex_initialised
    if not _vertex_initialised:
        try:
            import vertexai
            vertexai.init(
                project=settings.GCP_PROJECT_ID,
                location=settings.VERTEX_AI_LOCATION,
            )
            _vertex_initialised = True
            log.info("Vertex AI initialised (project=%s, location=%s)",
                     settings.GCP_PROJECT_ID, settings.VERTEX_AI_LOCATION)
        except Exception as exc:
            log.warning("Vertex AI init failed: %s", exc)


# ── Text Generation ───────────────────────────────────────────────────────────

def generate_campaign_copy(
    brand_name: str,
    campaign_name: str,
    campaign_objective: str,
    tone: str = "professional",
    model: str = "gemini-1.5-pro",
) -> Optional[str]:
    """Generate marketing copy for a campaign using Gemini on Vertex AI."""
    _init_vertex()
    prompt = (
        f"You are a creative marketing expert for {brand_name}.\n"
        f"Write compelling campaign copy for the '{campaign_name}' campaign.\n"
        f"Objective: {campaign_objective}\n"
        f"Tone: {tone}\n"
        f"Provide a headline, tagline, and 3-sentence body copy."
    )
    try:
        from vertexai.generative_models import GenerativeModel
        model_obj = GenerativeModel(model)
        response = model_obj.generate_content(prompt)
        return response.text
    except Exception as exc:
        log.error("generate_campaign_copy error: %s", exc)
        return None


# ── Image Generation (Imagen) ─────────────────────────────────────────────────

def generate_image(
    prompt: str,
    campaign_id: str,
    model: str = "imagegeneration@006",
    aspect_ratio: str = "1:1",
    number_of_images: int = 1,
) -> list[bytes]:
    """Generate images using Imagen on Vertex AI. Returns list of PNG bytes."""
    _init_vertex()
    try:
        from vertexai.preview.vision_models import ImageGenerationModel
        model_obj = ImageGenerationModel.from_pretrained(model)
        response = model_obj.generate_images(
            prompt=prompt,
            number_of_images=number_of_images,
            aspect_ratio=aspect_ratio,
        )
        images_bytes = []
        for img in response.images:
            images_bytes.append(img._image_bytes)
        log.info("Generated %d image(s) for campaign %s", len(images_bytes), campaign_id)
        return images_bytes
    except Exception as exc:
        log.error("generate_image error: %s", exc)
        return []


# ── Prompt Templates ─────────────────────────────────────────────────────────

def build_brand_aware_prompt(
    brand_name: str,
    brand_tone: str,
    brand_description: str,
    target_audience: str,
    task: str,
) -> str:
    """Build a brand-aware prompt for any generative AI task."""
    return (
        f"Brand: {brand_name}\n"
        f"Description: {brand_description}\n"
        f"Tone: {brand_tone}\n"
        f"Target Audience: {target_audience}\n\n"
        f"Task: {task}"
    )
