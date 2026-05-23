import os

# Ensure config imports succeed in CI/local test runs without a real Redis URL.
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

import pytest

from backend.services.notion_service import NotionService
from backend.services.redis_service import RedisService


@pytest.fixture(autouse=True)
def reset_service_singletons():
    """Isolate tests from singleton state and live Redis connections."""
    NotionService._instance = None
    RedisService._instance = None
    RedisService._pool = None
    yield
    NotionService._instance = None
    RedisService._instance = None
    RedisService._pool = None


@pytest.fixture
def mock_redis_service(mocker):
    redis_service = mocker.MagicMock()
    redis_service.get_cache_key.return_value = "cryptids"
    redis_service.exists.return_value = True
    mocker.patch(
        "backend.services.notion_service.RedisService",
        return_value=redis_service,
    )
    return redis_service
