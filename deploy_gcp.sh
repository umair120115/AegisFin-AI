#!/bin/bash
set -e

PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "aegisfin-prod")
REGION="asia-south1" # Mumbai region for low-latency Indian UPI/FinTech workloads

echo "=========================================================="
echo " AegisFin-Core: Google Cloud Run Deployment Pipeline"
echo " Target Project: $PROJECT_ID | Region: $REGION"
echo "=========================================================="

echo "[1/4] Enabling Required Google Cloud APIs..."
gcloud services enable run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  aiplatform.googleapis.com

echo "[2/4] Deploying Backend API to Cloud Run..."
gcloud run deploy aegisfin-api \
  --source ./backend \
  --region $REGION \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 1 \
  --max-instances 10

BACKEND_URL=$(gcloud run services describe aegisfin-api --region $REGION --format 'value(status.url)')
echo "[+] Backend deployed at: $BACKEND_URL"

echo "[3/4] Deploying Frontend Security Command Center to Cloud Run..."
gcloud run deploy aegisfin-dashboard \
  --source ./frontend \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars="VITE_API_BASE_URL=$BACKEND_URL"

FRONTEND_URL=$(gcloud run services describe aegisfin-dashboard --region $REGION --format 'value(status.url)')
echo "[+] Frontend deployed at: $FRONTEND_URL"
echo "=========================================================="
echo "Deployment Complete! Command Center is live at $FRONTEND_URL"
echo "=========================================================="
