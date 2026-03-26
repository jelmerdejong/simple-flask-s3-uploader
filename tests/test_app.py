from __future__ import annotations

import io

import boto3

from s3_uploader import create_app

from .conftest import extract_csrf_token


def test_create_app_does_not_initialize_boto3_client(monkeypatch):
    calls: list[tuple[str, dict[str, str]]] = []

    def fake_client(service_name: str, **kwargs: str):
        calls.append((service_name, kwargs))
        raise AssertionError("boto3.client should not be called during app creation")

    monkeypatch.setattr(boto3, "client", fake_client)

    app = create_app({"LOAD_DOTENV": False, "SECRET_KEY": "test-secret-key", "TESTING": True})

    assert app is not None
    assert calls == []


def test_index_renders_form_and_csrf_token(client):
    response = client.get("/")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Upload a file" in html
    assert 'name="csrf_token"' in html
    assert "bootstrap@5.3.8" in html


def test_upload_redirects_to_result_page(client, storage_service):
    csrf_token = extract_csrf_token(client.get("/").get_data(as_text=True))

    response = client.post(
        "/upload",
        data={
            "csrf_token": csrf_token,
            "user_file": (io.BytesIO(b"hello world"), "hello.txt"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert storage_service.calls == ["hello.txt"]
    assert "File uploaded successfully." in html
    assert "https://example-bucket.s3.amazonaws.com/hello.txt" in html


def test_upload_missing_file_field_returns_error(client):
    csrf_token = extract_csrf_token(client.get("/").get_data(as_text=True))

    response = client.post(
        "/upload",
        data={"csrf_token": csrf_token},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert "Missing file field in form submission." in response.get_data(as_text=True)


def test_upload_empty_filename_returns_error(client):
    csrf_token = extract_csrf_token(client.get("/").get_data(as_text=True))

    response = client.post(
        "/upload",
        data={
            "csrf_token": csrf_token,
            "user_file": (io.BytesIO(b""), ""),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert "Please choose a file to upload." in response.get_data(as_text=True)


def test_upload_disallowed_extension_returns_error(client):
    csrf_token = extract_csrf_token(client.get("/").get_data(as_text=True))

    response = client.post(
        "/upload",
        data={
            "csrf_token": csrf_token,
            "user_file": (io.BytesIO(b"boom"), "notes.exe"),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert "File type not allowed." in response.get_data(as_text=True)


def test_upload_requires_csrf_token(client):
    response = client.post(
        "/upload",
        data={"user_file": (io.BytesIO(b"hello world"), "hello.txt")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert "CSRF validation failed" in response.get_data(as_text=True)


def test_environment_variable_overrides_dotenv(monkeypatch, tmp_path):
    dotenv_path = tmp_path / ".env"
    dotenv_path.write_text("SECRET_KEY=from-dotenv\n", encoding="utf-8")
    monkeypatch.setenv("SECRET_KEY", "from-env")

    app = create_app(
        {
            "DOTENV_PATH": dotenv_path,
            "LOAD_DOTENV": True,
            "TESTING": True,
        }
    )

    assert app.config["SECRET_KEY"] == "from-env"
