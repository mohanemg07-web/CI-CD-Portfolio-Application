import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Ensure backend/ root is importable as `app` package
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import create_app  # noqa: E402


@pytest.fixture()
def client():
    app = create_app()
    with TestClient(app) as c:
        yield c
