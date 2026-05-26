import os

from dotenv import load_dotenv

load_dotenv()


APP_VERSION = "1.0.0"

ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",")
    if origin.strip()
]

BETTERSTACK_SOURCE_TOKEN = os.getenv("BETTERSTACK_SOURCE_TOKEN", "")
BETTERSTACK_INGEST_URL = os.getenv(
    "BETTERSTACK_INGEST_URL", "https://in.logs.betterstack.com"
)
