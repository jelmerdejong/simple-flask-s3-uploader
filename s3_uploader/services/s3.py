from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import quote

import boto3
from botocore.client import BaseClient
from botocore.exceptions import BotoCoreError, ClientError
from flask import Flask
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


class StorageError(RuntimeError):
    """Raised when an upload cannot be completed."""


class StorageConfigurationError(StorageError):
    """Raised when the storage client is not configured correctly."""


@dataclass
class S3StorageService:
    bucket_name: str | None
    region_name: str | None
    access_key_id: str | None
    secret_access_key: str | None
    object_acl: str | None = "public-read"
    public_url_base: str | None = None
    endpoint_url: str | None = None
    _client: BaseClient | None = field(default=None, init=False, repr=False)

    @classmethod
    def from_app(cls, app: Flask) -> "S3StorageService":
        return cls(
            bucket_name=app.config["S3_BUCKET"],
            region_name=app.config["AWS_DEFAULT_REGION"],
            access_key_id=app.config["AWS_ACCESS_KEY_ID"],
            secret_access_key=app.config["AWS_SECRET_ACCESS_KEY"],
            object_acl=app.config["S3_OBJECT_ACL"],
            public_url_base=app.config["S3_PUBLIC_URL_BASE"],
            endpoint_url=app.config["S3_ENDPOINT_URL"],
        )

    def upload(self, file_storage: FileStorage) -> str:
        if not self.bucket_name:
            raise StorageConfigurationError("S3_BUCKET is not configured.")

        filename = secure_filename(file_storage.filename or "")
        if not filename:
            raise StorageError("Unable to determine a safe filename for the upload.")

        extra_args = {
            "ContentType": file_storage.content_type or "application/octet-stream",
        }
        if self.object_acl:
            extra_args["ACL"] = self.object_acl

        try:
            self.client().upload_fileobj(
                file_storage.stream,
                self.bucket_name,
                filename,
                ExtraArgs=extra_args,
            )
        except (BotoCoreError, ClientError, ValueError) as exc:
            raise StorageError(f"Failed to upload file to S3: {exc}") from exc

        return self.public_url(filename)

    def client(self) -> BaseClient:
        if self._client is None:
            client_kwargs: dict[str, str] = {}
            if self.region_name:
                client_kwargs["region_name"] = self.region_name
            if self.endpoint_url:
                client_kwargs["endpoint_url"] = self.endpoint_url
            if self.access_key_id:
                client_kwargs["aws_access_key_id"] = self.access_key_id
            if self.secret_access_key:
                client_kwargs["aws_secret_access_key"] = self.secret_access_key

            self._client = boto3.client("s3", **client_kwargs)

        return self._client

    def public_url(self, object_key: str) -> str:
        encoded_key = quote(object_key)
        if self.public_url_base:
            return f"{self.public_url_base.rstrip('/')}/{encoded_key}"

        if self.region_name and self.region_name != "us-east-1":
            return f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{encoded_key}"

        return f"https://{self.bucket_name}.s3.amazonaws.com/{encoded_key}"
