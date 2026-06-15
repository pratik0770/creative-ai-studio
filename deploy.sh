#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────
# Creative AI Studio — GCP Deployment Script
# Usage: bash deploy.sh [PROJECT_ID] [REGION]
# ──────────────────────────────────────────────────────────────────
set -euo pipefail

PROJECT_ID="${1:-your-gcp-project-id}"
REGION="${2:-us-central1}"
SERVICE_NAME="creative-ai-studio"
IMAGE="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
SQL_INSTANCE="${PROJECT_ID}:${REGION}:creative-ai-studio-db"

echo "═══════════════════════════════════════════════════"
echo "  Deploying Creative AI Studio to Cloud Run"
echo "  Project : ${PROJECT_ID}"
echo "  Region  : ${REGION}"
echo "═══════════════════════════════════════════════════"

# 1. Enable required APIs
echo "→ Enabling GCP APIs..."
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  storage.googleapis.com \
  secretmanager.googleapis.com \
  identitytoolkit.googleapis.com \
  aiplatform.googleapis.com \
  cloudbuild.googleapis.com \
  --project="${PROJECT_ID}"

# 2. Build & push container
echo "→ Building and pushing Docker image..."
gcloud builds submit \
  --tag "${IMAGE}:latest" \
  --project="${PROJECT_ID}"

# 3. Store secrets in Secret Manager (run once)
echo "→ Storing secrets in Secret Manager..."
echo -n "${SECRET_KEY:-$(openssl rand -hex 32)}" | \
  gcloud secrets create creative-ai-studio-secret-key \
    --data-file=- --project="${PROJECT_ID}" 2>/dev/null || true

# 4. Deploy to Cloud Run
echo "→ Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
  --image "${IMAGE}:latest" \
  --platform managed \
  --region "${REGION}" \
  --project "${PROJECT_ID}" \
  --allow-unauthenticated \
  --port 8080 \
  --cpu 1 \
  --memory 512Mi \
  --min-instances 0 \
  --max-instances 10 \
  --concurrency 80 \
  --timeout 300 \
  --add-cloudsql-instances "${SQL_INSTANCE}" \
  --set-env-vars "GCP_PROJECT_ID=${PROJECT_ID}" \
  --set-env-vars "GCP_REGION=${REGION}" \
  --set-env-vars "CLOUD_SQL_INSTANCE=${SQL_INSTANCE}" \
  --set-env-vars "DB_NAME=creative_ai_studio" \
  --set-env-vars "DB_USER=creative_ai_user" \
  --set-secrets "SECRET_KEY=creative-ai-studio-secret-key:latest" \
  --set-secrets "DB_PASSWORD=creative-ai-studio-db-password:latest" \
  --set-secrets "FIREBASE_API_KEY=creative-ai-studio-firebase-key:latest"

echo ""
echo "✓ Deployment complete!"
gcloud run services describe "${SERVICE_NAME}" \
  --region="${REGION}" \
  --project="${PROJECT_ID}" \
  --format="value(status.url)"
