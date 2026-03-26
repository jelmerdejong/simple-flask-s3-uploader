from __future__ import annotations

from flask import Flask
from flask_wtf.csrf import CSRFProtect


csrf = CSRFProtect()


def init_extensions(app: Flask) -> None:
    csrf.init_app(app)
