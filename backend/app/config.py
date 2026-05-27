import os

from dotenv import load_dotenv

load_dotenv()


APP_VERSION = "1.0.0"

# Render / Railway inject $PORT at runtime; default to 8000 for local dev.
PORT = int(os.getenv("PORT", 8000))

# Origins that are always permitted, regardless of the ALLOWED_ORIGINS env var.
# Keeps prod Vercel + local dev working even if the env var is misconfigured.
_ALWAYS_ALLOWED = [
    "https://ci-cd-portfolio-application.vercel.app",
    "http://localhost",
    "http://localhost:80",
    "http://localhost:5173",
]

_env_origins = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]

# De-duplicate while preserving order.
_seen: set[str] = set()
ALLOWED_ORIGINS = [
    o for o in (_env_origins + _ALWAYS_ALLOWED) if not (o in _seen or _seen.add(o))
]

BETTERSTACK_SOURCE_TOKEN = os.getenv("BETTERSTACK_SOURCE_TOKEN", "")
BETTERSTACK_INGEST_URL = os.getenv(
    "BETTERSTACK_INGEST_URL", "https://in.logs.betterstack.com"
)
