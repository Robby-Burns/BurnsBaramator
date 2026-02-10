# Dependency Management Guide

## Overview

This project uses a flexible dependency management strategy to ensure stability while allowing for updates.

## Files

- `requirements.txt`: Main dependency file with flexible versions (e.g., `package>=1.0.0`).
- `Dockerfile`: Uses `requirements.txt` to build the container image.
- `pyproject.toml`: (Optional) For packaging and tool configuration.

## Adding Dependencies

1. Add the package to `requirements.txt`.
2. Run `uv pip install -r requirements.txt` (or `pip install`).
3. Update `Dockerfile` if system-level dependencies are needed.

## Best Practices

- **Never use `==`** for top-level dependencies unless strictly necessary (e.g., known breaking changes). Use `>=` to allow security patches.
- **Lock files:** For strict reproducibility in production, generate a `requirements-lock.txt` using `pip freeze > requirements-lock.txt`.
- **Virtual Environments:** Always use a virtual environment (`.venv`) locally.
