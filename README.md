# Simple Flask AWS S3 Uploader

[![CI](https://github.com/jelmerdejong/simple-flask-s3-uploader/actions/workflows/ci.yml/badge.svg)](https://github.com/jelmerdejong/simple-flask-s3-uploader/actions/workflows/ci.yml)
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/jelmerdejong/simple-flask-s3-uploader)

A modern Flask 3.1 application for uploading files to Amazon S3. The app now uses an application factory, CSRF-protected forms, lazy S3 client creation, Bootstrap 5.3, and hermetic pytest coverage.

## Stack

- Python 3.11+
- Flask 3.1
- Flask-WTF with CSRF protection
- Boto3 for S3 uploads
- `uv` for dependency management and locking
- pytest for the test suite

This project intentionally stays database-free. There is no SQLAlchemy setup, no migrations, and no Postgres dependency.

## Quick Start

1. Install `uv` if it is not already available.
2. Sync the project environment:

   ```bash
   uv sync --group dev
   ```

3. Create a local environment file:

   ```bash
   cp .env.example .env
   ```

4. Edit `.env` with your AWS bucket and credentials.
5. Run the development server:

   ```bash
   uv run flask --app 's3_uploader:create_app' run --debug
   ```

6. Open [http://127.0.0.1:5000](http://127.0.0.1:5000).

The repository also keeps a compatibility shim in [`app.py`](app.py), so `flask --app app run` still works if you need it.

## Configuration

The app loads configuration in this order:

1. Defaults defined in code.
2. `.env` values loaded with `python-dotenv`.
3. Real environment variables.
4. Test overrides passed into `create_app(...)`.

Real environment variables always win over `.env`.

Supported settings:

- `SECRET_KEY`: Required outside tests for Flask session and CSRF signing.
- `S3_BUCKET`: Destination bucket name.
- `AWS_ACCESS_KEY_ID`: Preferred AWS access key setting.
- `AWS_SECRET_ACCESS_KEY`: Preferred AWS secret key setting.
- `AWS_DEFAULT_REGION`: Region used for the boto3 client and public S3 URL generation.
- `S3_OBJECT_ACL`: Optional object ACL. Default is `public-read`.
- `S3_PUBLIC_URL_BASE`: Optional explicit base URL for uploaded objects.
- `S3_ENDPOINT_URL`: Optional S3-compatible endpoint override.

Legacy `S3_KEY` and `S3_SECRET_ACCESS_KEY` variables are still accepted as fallbacks.

## Testing

Run the full suite with:

```bash
uv run pytest
```

The tests do not talk to AWS. Upload behavior is validated with Flask’s test client and a mocked storage service.

## Production Run

Use Gunicorn with the application factory:

```bash
uv run gunicorn 's3_uploader:create_app()'
```

## Codespaces

This repository includes a minimal devcontainer. In GitHub Codespaces, the container installs `uv`, syncs the locked environment, and exposes port `5000` for the Flask app.
