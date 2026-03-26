from __future__ import annotations

from collections.abc import Iterable

from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from werkzeug.datastructures import FileStorage
from wtforms import SubmitField
from wtforms.validators import ValidationError


class UploadForm(FlaskForm):
    user_file = FileField("Upload a file")
    submit = SubmitField("Upload")

    def __init__(self, *args: object, allowed_extensions: Iterable[str], **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.allowed_extensions = {extension.lower().lstrip(".") for extension in allowed_extensions}

    def validate_user_file(self, field: FileField) -> None:
        if field.data is None:
            raise ValidationError("Missing file field in form submission.")

        if not isinstance(field.data, FileStorage):
            raise ValidationError("Invalid file upload.")

        filename = field.data.filename or ""
        if not filename.strip():
            raise ValidationError("Please choose a file to upload.")

        if "." not in filename:
            raise ValidationError("File type not allowed.")

        extension = filename.rsplit(".", 1)[1].lower()
        if extension not in self.allowed_extensions:
            raise ValidationError("File type not allowed.")
