#!/usr/bin/env bash
set -euo pipefail

# -------------------------------------------------------------------
# Portfolio App deploy script — pushes backend + frontend to Railway.
# Requires: RAILWAY_TOKEN env var (Railway → Account → Tokens).
# -------------------------------------------------------------------

if ! command -v railway >/dev/null 2>&1; then
  echo "→ Railway CLI not found. Installing via npm..."
  if ! command -v npm >/dev/null 2>&1; then
    echo "✗ npm is required to install the Railway CLI. Install Node 20+ first." >&2
    exit 1
  fi
  npm install -g @railway/cli
fi

if [[ -z "${RAILWAY_TOKEN:-}" ]]; then
  echo "✗ RAILWAY_TOKEN is not set." >&2
  echo "  Create one at https://railway.app/account/tokens and export it:" >&2
  echo "    export RAILWAY_TOKEN=xxxxxxxx" >&2
  exit 1
fi

export RAILWAY_TOKEN

echo "→ Authenticating with Railway (browserless)..."
railway login --browserless >/dev/null 2>&1 || true

deploy_service() {
  local service="$1"
  local config="$2"
  echo "→ Deploying ${service} using ${config}..."
  railway up --service "${service}" --config "${config}" --detach
  railway status --json 2>/dev/null \
    | (command -v jq >/dev/null 2>&1 \
        && jq -r '.deployments[0].url // .url // empty' \
        || grep -Eo 'https?://[^"]+' | head -n 1) \
    | head -n 1
}

BACKEND_URL=$(deploy_service backend railway.toml || true)
FRONTEND_URL=$(deploy_service frontend railway.frontend.toml || true)

echo ""
echo "==================== DEPLOYMENT COMPLETE ===================="
echo "Backend:  ${BACKEND_URL:-<unknown - check Railway dashboard>}"
echo "Frontend: ${FRONTEND_URL:-<unknown - check Railway dashboard>}"
echo "============================================================="
