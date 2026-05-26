# Portfolio App — Full-Stack DevOps Demo

[![CI/CD Pipeline](https://github.com/mohanemg07-web/portfolio-app/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/mohanemg07-web/portfolio-app/actions/workflows/ci-cd.yml)
[![Uptime](https://uptime.betterstack.com/status-badges/v3/monitor/replace-me.svg)](https://betterstack.com/uptime)
[![Python](https://img.shields.io/badge/python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-18-61DAFB?logo=react&logoColor=white)](https://react.dev/)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

---

## 1. Project Overview

This repository is a production-grade portfolio site that demonstrates the
**full DevOps loop**: a React frontend and Python FastAPI backend, packaged into
multi-stage Docker images, automatically linted/tested/built/deployed by GitHub
Actions, instrumented with Prometheus, dashboarded in Grafana Cloud, log-shipped
to Better Stack, and monitored with HTTP uptime checks. Every push to `main`
flows through a four-stage pipeline that completes in under four minutes thanks
to layered caching at the pip, npm, and Docker buildx layers.

The codebase doubles as a working showcase of **defense-in-depth DevOps
practices**: non-root containers with HEALTHCHECK probes, request-level
structured JSON logging with per-request UUIDs, Prometheus histograms wired into
`p95` Grafana panels, an OpenAI-powered PR summary bot that flags breaking
changes, and infra-as-config Railway manifests so a single `deploy.sh` push
brings up both services with health-gated rollouts. Nothing is mocked — every
moving part is genuine code you can clone and run today.

---

## 2. Architecture

```
                     ┌──────────────────────────────────────────┐
                     │              GitHub PR / push            │
                     └─────────────┬────────────────────────────┘
                                   │
                                   ▼
                  ┌────────────────────────────────────┐
                  │          GitHub Actions            │
                  │  lint → test → docker-build → deploy │
                  └─────┬──────────────────┬───────────┘
                        │                  │
                        ▼                  ▼
                ┌──────────────┐   ┌──────────────────┐
                │  Docker Hub  │   │     Railway      │
                └──────────────┘   └──────┬───────────┘
                                          │
              ┌───────────────────────────┼───────────────────────┐
              ▼                           ▼                       ▼
       ┌─────────────┐           ┌─────────────────┐      ┌──────────────┐
       │  Browser    │ ───────►  │ Frontend (nginx)│ ───► │ Backend      │
       │ (user)      │           │ React SPA       │ /api │ FastAPI      │
       └─────────────┘           └─────────────────┘      └────┬─────────┘
                                                               │
                                ┌──────────────────────────────┼────────────────────┐
                                ▼                              ▼                    ▼
                         ┌─────────────┐               ┌────────────────┐   ┌──────────────┐
                         │  /metrics   │               │  Better Stack  │   │ Better Stack │
                         │  (Prom)     │ ───────────►  │  Logs          │   │ Uptime       │
                         └──────┬──────┘               └────────────────┘   └──────────────┘
                                ▼
                         ┌──────────────┐
                         │ Grafana Cloud│
                         │   3 panels   │
                         └──────────────┘
```

---

## 3. Local Development

### Prerequisites

- Docker 24+ and Docker Compose
- Node 20+
- Python 3.11

### Run it

```bash
git clone https://github.com/mohanemg07-web/portfolio-app.git
cd portfolio-app

cp frontend/.env.example frontend/.env
# optional — only if you want logs shipped to Better Stack locally
# echo 'BETTERSTACK_SOURCE_TOKEN=xxxxx' >> .env

docker-compose up --build
```

Then open:

- Frontend: **http://localhost**
- Backend health: **http://localhost:8000/health**
- Prometheus metrics: **http://localhost:8000/metrics**

### Run backend tests directly

```bash
cd backend
pip install -r requirements.txt
pytest --cov=app --cov-report=term-missing
```

### Run frontend dev server (hot reload)

```bash
cd frontend
npm install
npm run dev   # http://localhost:5173
```

---

## 4. CI/CD Pipeline

```
   ┌──────┐    ┌──────┐    ┌──────────────┐    ┌────────┐
   │ lint │ ─► │ test │ ─► │ docker-build │ ─► │ deploy │
   └──────┘    └──────┘    └──────────────┘    └────────┘
   ruff +      pytest +     buildx + push     railway up
   eslint      coverage     to Docker Hub     to Railway
```

| Stage          | What it does                                                              | Cache key                                |
|----------------|---------------------------------------------------------------------------|------------------------------------------|
| `lint`         | `ruff check ./backend` and `npm run lint` in `frontend/`                  | `pip` on `requirements.txt`, `npm` on `package-lock.json` |
| `test`         | `pytest --cov=app --cov-report=xml`, uploads `coverage.xml` artifact       | reuses `pip` cache                       |
| `docker-build` | buildx-builds both images, pushes to Docker Hub tagged with `${{ github.sha }}` | `type=gha` cache scoped per image       |
| `deploy`       | Runs on `main` only — `railway up` for backend and frontend services      | n/a                                      |

### How it stays under 4 minutes

- **pip + npm caches** hit on most runs, skipping ~90 s of installs.
- **Buildx GHA cache** keeps Docker layers warm across runs, so only changed layers rebuild.
- Lint and test only re-run when their inputs change (cache short-circuits restore).

---

## 5. PR Automation Bot

The [`pr-summary.yml`](./.github/workflows/pr-summary.yml) workflow runs on
every `pull_request: [opened, synchronize]` and posts an AI-generated review:

1. Checks out with `fetch-depth: 0` and runs `git diff origin/main...HEAD`.
2. Sends the diff to `gpt-4o-mini` via `curl`, asking for a strict JSON object
   with `summary`, `breaking_changes`, and `risk_level`.
3. Parses the response in `actions/github-script@v7` and posts a comment:

   > ## PR Summary
   > ### What Changed
   > _one paragraph_
   > ### Breaking Changes
   > - bullets, or "None"
   > ### Risk Level
   > 🟢 low / 🟡 medium / 🔴 high

4. If `breaking_changes` is non-empty, adds the `breaking-change` label.
5. On any failure, posts a fallback `PR summary unavailable` comment so the PR
   thread isn't left silent.

### Setup

Add the OpenAI key as a repo secret:

```
Repo → Settings → Secrets and variables → Actions → New repository secret
Name:  OPENAI_API_KEY
Value: sk-...
```

---

## 6. Monitoring

### Grafana Cloud

1. **Sign up at https://grafana.com/products/cloud/** and create a stack.
2. In Grafana → **Connections → Data sources → Add data source → Prometheus**.
3. Point it at a Prometheus instance scraping your Railway backend:

   ```yaml
   # prometheus.yml (Grafana Cloud Hosted Prometheus or self-hosted)
   scrape_configs:
     - job_name: portfolio-backend
       metrics_path: /metrics
       scheme: https
       static_configs:
         - targets: ['<your-railway-backend>.up.railway.app']
       scrape_interval: 30s
   ```

4. Grafana → **Dashboards → Import** → upload [`grafana/dashboard.json`](./grafana/dashboard.json).
5. Select the Prometheus data source when prompted; the three panels
   (throughput, error rate, p95 latency) will populate automatically.

### Better Stack

Full step-by-step: [`betterstack/setup.md`](./betterstack/setup.md).

Quick summary: one HTTP uptime monitor against `/health` (1-min frequency,
1-min downtime threshold), email-then-SMS escalation, plus a Logs source whose
token becomes the `BETTERSTACK_SOURCE_TOKEN` env var on Railway.

---

## 7. Environment Variables

| Variable                    | Required                          | Default                  | Description                                                                 |
|-----------------------------|-----------------------------------|--------------------------|-----------------------------------------------------------------------------|
| `ALLOWED_ORIGINS`           | No                                | `*`                      | Comma-separated CORS origins for the FastAPI backend.                       |
| `BETTERSTACK_SOURCE_TOKEN`  | No (recommended in prod)          | unset (no-op)            | Better Stack Logs source token. When set, every request log is shipped.     |
| `BETTERSTACK_INGEST_URL`    | No                                | `https://in.logs.betterstack.com` | Override the Better Stack ingestion URL (rarely needed).         |
| `PORT`                      | Auto (Railway)                    | `8000`                   | Railway injects `$PORT`; used in `startCommand`.                            |
| `VITE_API_URL`              | Yes (frontend)                    | `http://localhost:8000`  | Base URL the React app calls. Set per environment.                          |
| `DOCKERHUB_USERNAME`        | Yes (GitHub Actions)              | —                        | Docker Hub username for image push.                                         |
| `DOCKERHUB_TOKEN`           | Yes (GitHub Actions)              | —                        | Docker Hub access token.                                                    |
| `RAILWAY_TOKEN`             | Yes (GitHub Actions / `deploy.sh`)| —                        | Railway account/project token used to deploy.                               |
| `OPENAI_API_KEY`            | Yes (PR summary workflow)         | —                        | OpenAI API key for the GPT-4o-mini PR summary bot.                          |

---

## 8. Deployment

1. **Authenticate once locally:**

   ```bash
   export RAILWAY_TOKEN=xxxxxxxxxxxx
   ```

2. **Run the deploy script:**

   ```bash
   # macOS / Linux
   chmod +x deploy.sh
   ./deploy.sh

   # Windows
   bash deploy.sh
   ```

   The script installs the Railway CLI if missing, validates `RAILWAY_TOKEN`,
   then pushes the `backend` and `frontend` services using `railway.toml` and
   `railway.frontend.toml`. At the end it prints both deployed URLs:

   ```
   Backend:  https://portfolio-backend-production.up.railway.app
   Frontend: https://portfolio-frontend-production.up.railway.app
   ```

3. **Production rollouts** happen automatically through the [`ci-cd.yml`](./.github/workflows/ci-cd.yml)
   workflow on every push to `main`. The `deploy.sh` script exists for local
   re-deploys and one-off bootstrapping.

---

## 9. Repository Layout

```
.
├── backend/                   FastAPI app + tests
│   ├── app/
│   │   ├── main.py            App factory, lifespan, Prometheus wiring
│   │   ├── config.py          Env-var loading
│   │   ├── routes/            health, projects, metrics
│   │   └── middleware/        timing, cors, structured JSON logging
│   └── tests/                 9 pytest tests covering all routes
├── frontend/                  React + Vite SPA
│   └── src/                   App.jsx, main.jsx, index.css
├── grafana/dashboard.json     Importable Grafana dashboard (3 panels)
├── betterstack/setup.md       Uptime monitor + log drain setup guide
├── .github/workflows/
│   ├── ci-cd.yml              lint → test → docker-build → deploy
│   └── pr-summary.yml         GPT-4o-mini PR review bot
├── Dockerfile.backend         Multi-stage, non-root, HEALTHCHECK
├── Dockerfile.frontend        node build → nginx serve
├── nginx.conf                 SPA fallback + /api proxy
├── docker-compose.yml         Local dev stack
├── railway.toml               Backend service config
├── railway.frontend.toml      Frontend service config
└── deploy.sh                  One-shot Railway deploy script
```

---

## License

MIT. Replace placeholder name, links, and Docker Hub username before publishing.
