from __future__ import annotations

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_wtf.csrf import CSRFError

from .forms import UploadForm
from .services.s3 import StorageError


bp = Blueprint("main", __name__)


@bp.get("/")
def index():
    return render_template(
        "index.html",
        form=_build_form(),
        allowed_extensions=current_app.config["ALLOWED_EXTENSIONS"],
        uploaded_url=request.args.get("uploaded"),
    )


@bp.post("/upload")
def upload():
    form = _build_form()
    uploaded_file = request.files.get(form.user_file.name)

    if uploaded_file is not None and uploaded_file.filename == "":
        form.user_file.errors = ["Please choose a file to upload."]
        return (
            render_template(
                "index.html",
                form=form,
                allowed_extensions=current_app.config["ALLOWED_EXTENSIONS"],
                uploaded_url=None,
            ),
            400,
        )

    if not form.validate_on_submit():
        return (
            render_template(
                "index.html",
                form=form,
                allowed_extensions=current_app.config["ALLOWED_EXTENSIONS"],
                uploaded_url=None,
            ),
            400,
        )

    storage_service = current_app.extensions["storage_service"]
    try:
        uploaded_url = storage_service.upload(form.user_file.data)
    except StorageError as exc:
        form.user_file.errors.append(str(exc))
        return (
            render_template(
                "index.html",
                form=form,
                allowed_extensions=current_app.config["ALLOWED_EXTENSIONS"],
                uploaded_url=None,
            ),
            502,
        )

    flash("File uploaded successfully.", "success")
    return redirect(url_for("main.index", uploaded=uploaded_url))


@bp.app_errorhandler(CSRFError)
def handle_csrf_error(error: CSRFError):
    flash(f"CSRF validation failed: {error.description}", "danger")
    return (
        render_template(
            "index.html",
            form=_build_form(),
            allowed_extensions=current_app.config["ALLOWED_EXTENSIONS"],
            uploaded_url=None,
        ),
        400,
    )


def _build_form() -> UploadForm:
    return UploadForm(allowed_extensions=current_app.config["ALLOWED_EXTENSIONS"])
