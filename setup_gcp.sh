#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────
# Creative AI Studio — GCP Infrastructure Setup (run once)
# Usage: bash setup_gcp.sh [PROJECT_ID] [REGION]
# ──────────────────────────────────────────────────────────────────
set -euo pipefail

PROJECT_ID="${1:-your-gcp-project-id}"
REGION="${2:-us-central1}"
DB_INSTANCE="creative-ai-studio-db"
DB_NAME="creative_ai_studio"
DB_USER="creative_ai_user"
GCS_BUCKET="${PROJECT_ID}-creative-ai-studio-assets"

echo "Setting up GCP infrastructure for Creative AI Studio..."
echo "Project: ${PROJECT_ID} | Region: ${REGION}"

# ── Cloud SQL ──────────────────────────────────────────────────────
echo "→ Creating Cloud SQL (PostgreSQL 15) instance..."
gcloud sql instances create "${DB_INSTANCE}" \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region="${REGION}" \
  --project="${PROJECT_ID}" \
  --storage-type=SSD \
  --storage-size=10GB \
  --backup-start-time=02:00 \
  --require-ssl

echo "→ Creating database and user..."
gcloud sql databases create "${DB_NAME}" \
  --instance="${DB_INSTANCE}" \
  --project="${PROJECT_ID}"

DB_PASSWORD=$(openssl rand -base64 20)
gcloud sql users create "${DB_USER}" \
  --instance="${DB_INSTANCE}" \
  --password="${DB_PASSWORD}" \
  --project="${PROJECT_ID}"

# Store DB password in Secret Manager
echo -n "${DB_PASSWORD}" | gcloud secrets create creative-ai-studio-db-password \
  --data-file=- --project="${PROJECT_ID}"

echo "✓ Cloud SQL ready: ${PROJECT_ID}:${REGION}:${DB_INSTANCE}"

# ── GCS Bucket ────────────────────────────────────────────────────
echo "→ Creating Cloud Storage bucket..."
gcloud storage buckets create "gs://${GCS_BUCKET}" \
  --project="${PROJECT_ID}" \
  --location="${REGION}" \
  --uniform-bucket-level-access

echo "✓ GCS bucket: gs://${GCS_BUCKET}"

# ── Service Account ────────────────────────────────────────────────
echo "→ Creating service account for Cloud Run..."
gcloud iam service-accounts create creative-ai-studio-sa \
  --display-name="Creative AI Studio Service Account" \
  --project="${PROJECT_ID}"

SA_EMAIL="creative-ai-studio-sa@${PROJECT_ID}.iam.gserviceaccount.com"

# Grant required roles
for ROLE in \
  roles/cloudsql.client \
  roles/storage.objectAdmin \
  roles/secretmanager.secretAccessor \
  roles/aiplatform.user \
  roles/logging.logWriter \
  roles/monitoring.metricWriter; do
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="${ROLE}" --quiet
done

echo "✓ Service account: ${SA_EMAIL}"

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  Infrastructure setup complete!"
echo ""
echo "  Next steps:"
echo "  1. Set FIREBASE_API_KEY in Secret Manager:"
echo "     echo -n 'YOUR_KEY' | gcloud secrets create creative-ai-studio-firebase-key --data-file=- --project=${PROJECT_ID}"
echo ""
echo "  2. Configure Firebase project at https://console.firebase.google.com"
echo "     Enable Email/Password authentication"
echo ""
echo "  3. Run: bash deploy.sh ${PROJECT_ID} ${REGION}"
echo "═══════════════════════════════════════════════════════"
