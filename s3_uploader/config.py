from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from flask import Flask


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ALLOWED_EXTENSIONS = ("txt", "pdf", "png", "jpg", "jpeg", "gif")

DEFAULT_CONFIG: dict[str, Any] = {
    "ALLOWED_EXTENSIONS": DEFAULT_ALLOWED_EXTENSIONS,
    "AWS_ACCESS_KEY_ID": None,
    "AWS_DEFAULT_REGION": "us-east-1",
    "AWS_SECRET_ACCESS_KEY": None,
    "DOTENV_PATH": PROJECT_ROOT / ".env",
    "LOAD_DOTENV": True,
    "MAX_CONTENT_LENGTH": 16 * 1024 * 1024,
    "S3_BUCKET": None,
    "S3_ENDPOINT_URL": None,
    "S3_OBJECT_ACL": "public-read",
    "S3_PUBLIC_URL_BASE": None,
    "SECRET_KEY": "dev-secret-key-change-me",
    "TESTING": False,
    "WTF_CSRF_ENABLED": True,
}

ENVIRONMENT_CONFIG = {
    "ALLOWED_EXTENSIONS": ("ALLOWED_EXTENSIONS",),
    "AWS_ACCESS_KEY_ID": ("AWS_ACCESS_KEY_ID", "S3_KEY"),
    "AWS_DEFAULT_REGION": ("AWS_DEFAULT_REGION", "AWS_REGION", "S3_REGION"),
    "AWS_SECRET_ACCESS_KEY": ("AWS_SECRET_ACCESS_KEY", "S3_SECRET_ACCESS_KEY"),
    "S3_BUCKET": ("S3_BUCKET",),
    "S3_ENDPOINT_URL": ("S3_ENDPOINT_URL",),
    "S3_OBJECT_ACL": ("S3_OBJECT_ACL",),
    "S3_PUBLIC_URL_BASE": ("S3_PUBLIC_URL_BASE",),
    "SECRET_KEY": ("SECRET_KEY",),
}


def load_environment_config(app: Flask) -> None:
    for config_key, env_names in ENVIRONMENT_CONFIG.items():
        value = _first_environment_value(env_names)
        if value is None:
            continue

        if config_key == "ALLOWED_EXTENSIONS":
            app.config[config_key] = tuple(_normalize_extensions(value.split(",")))
            continue

        app.config[config_key] = value


def _first_environment_value(names: tuple[str, ...]) -> str | None:
    for name in names:
        if name not in os.environ:
            continue

        value = os.environ[name]
        if value != "" or name == "S3_OBJECT_ACL":
            return value
    return None


def _normalize_extensions(values: list[str]) -> tuple[str, ...]:
    return tuple(extension.strip().lower().lstrip(".") for extension in values if extension.strip())
