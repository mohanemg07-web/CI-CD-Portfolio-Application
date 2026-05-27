from fastapi import APIRouter

router = APIRouter()

PROJECTS = [
    {
        "id": 1,
        "title": "DevOps Portfolio Platform",
        "description": (
            "Full-stack portfolio with CI/CD pipeline, container orchestration, "
            "metrics, and AI-assisted PR reviews."
        ),
        "tech_stack": ["React", "FastAPI", "Docker", "GitHub Actions", "Railway"],
        "github_url": "https://github.com/mohanemg07-web/CI-CD-Portfolio-Application",
        "live_url": "https://ci-cd-portfolio-application.vercel.app",
        "year": 2026,
    },
    {
        "id": 2,
        "title": "Realtime Metrics Pipeline",
        "description": (
            "Prometheus-instrumented FastAPI service exporting throughput, "
            "error rate, and p95 latency to Grafana Cloud."
        ),
        "tech_stack": ["FastAPI", "Prometheus", "Grafana", "Python"],
        "github_url": "https://github.com/mohanemg07-web/CI-CD-Portfolio-Application",
        "live_url": "https://portfolio-backend-cw15.onrender.com/metrics",
        "year": 2025,
    },
    {
        "id": 3,
        "title": "Observability Stack",
        "description": (
            "Structured JSON logging shipped to Better Stack with uptime "
            "monitoring and incident escalation."
        ),
        "tech_stack": ["Python", "Better Stack", "Docker", "Nginx"],
        "github_url": "https://github.com/mohanemg07-web/CI-CD-Portfolio-Application",
        "live_url": "https://portfolio-backend-cw15.onrender.com/health",
        "year": 2025,
    },
    {
        "id": 4,
        "title": "AI Code Review Bot",
        "description": (
            "GitHub Action that uses GPT-4o-mini to summarize PR diffs, "
            "flag breaking changes, and post structured reviews."
        ),
        "tech_stack": ["GitHub Actions", "OpenAI", "Node", "Bash"],
        "github_url": "https://github.com/mohanemg07-web/CI-CD-Portfolio-Application",
        "live_url": "https://github.com/mohanemg07-web/CI-CD-Portfolio-Application/blob/main/.github/workflows/pr-summary.yml",
        "year": 2024,
    },
]


@router.get("/projects")
async def list_projects() -> list[dict]:
    return PROJECTS
