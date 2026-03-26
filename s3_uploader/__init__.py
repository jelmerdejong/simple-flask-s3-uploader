from __future__ import annotations

from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from flask import Flask

from .config import DEFAULT_CONFIG, load_environment_config
from .extensions import init_extensions
from .services.s3 import S3StorageService


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(DEFAULT_CONFIG)

    test_config = test_config or {}
    dotenv_path = Path(test_config.get("DOTENV_PATH", app.config["DOTENV_PATH"]))
    load_dotenv_enabled = test_config.get("LOAD_DOTENV", app.config["LOAD_DOTENV"])

    if load_dotenv_enabled:
        load_dotenv(dotenv_path, override=False)

    load_environment_config(app)
    app.config.update(test_config)

    init_extensions(app)
    app.extensions["storage_service"] = S3StorageService.from_app(app)

    from .views import bp

    app.register_blueprint(bp)
    return app
