from __future__ import annotations

import re

import pytest

from s3_uploader import create_app


class DummyStorageService:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def upload(self, file_storage) -> str:
        filename = file_storage.filename or "uploaded-file"
        self.calls.append(filename)
        return f"https://example-bucket.s3.amazonaws.com/{filename}"


@pytest.fixture()
def app(monkeypatch: pytest.MonkeyPatch):
    for env_name in (
        "ALLOWED_EXTENSIONS",
        "AWS_ACCESS_KEY_ID",
        "AWS_DEFAULT_REGION",
        "AWS_SECRET_ACCESS_KEY",
        "S3_BUCKET",
        "S3_ENDPOINT_URL",
        "S3_KEY",
        "S3_OBJECT_ACL",
        "S3_PUBLIC_URL_BASE",
        "S3_REGION",
        "S3_SECRET_ACCESS_KEY",
        "SECRET_KEY",
    ):
        monkeypatch.delenv(env_name, raising=False)

    app = create_app(
        {
            "LOAD_DOTENV": False,
            "SECRET_KEY": "test-secret-key",
            "S3_BUCKET": "example-bucket",
            "TESTING": True,
            "WTF_CSRF_ENABLED": True,
        }
    )
    app.extensions["storage_service"] = DummyStorageService()
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def storage_service(app) -> DummyStorageService:
    return app.extensions["storage_service"]


def extract_csrf_token(html: str) -> str:
    match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', html)
    if not match:
        raise AssertionError("Unable to find a CSRF token in the response HTML.")
    return match.group(1)
