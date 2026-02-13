# Deployment Guide

## Architecture Overview

This system uses a **Worker** architecture to handle heavy processing.

1.  **The Worker:** Runs `main.py`. Scrapes jobs, analyzes fit, generates PDFs. Runs 24/7.
    *   *Supported Platforms:* **Railway** or **Fly.io**.
2.  **The Database (Neon):** Central PostgreSQL database.

---

## 1. Database Setup (Neon)

1.  Create a project at [Neon.tech](https://neon.tech).
2.  Copy the **Connection String** (e.g., `postgresql://user:pass@...`).
3.  You will need this for deployment.

---

## 2. Deployment Options

### Option A: Railway (Recommended)
1.  **Sign up** at [Railway.app](https://railway.app).
2.  **New Project** -> **Deploy from GitHub repo**.
3.  Select this repository.
4.  **Variables:** Add the following environment variables in Railway:
    *   `DATABASE_URL`: (Your Neon connection string)
    *   `ANTHROPIC_API_KEY`: (Your API key)
    *   `CLOUD_MODE`: `true` (Enables 24/7 scheduler)
5.  **Deploy.** Railway will automatically detect the `Dockerfile`.

### Option B: Fly.io
1.  Install `flyctl`.
2.  Login: `fly auth login`.
3.  Launch: `fly launch` (It will detect `fly.toml`).
4.  Set Secrets:
    ```bash
    fly secrets set DATABASE_URL=... ANTHROPIC_API_KEY=...
    ```
5.  Deploy: `fly deploy`.

---

## 3. Local Development

1.  Create `.env` with your keys.
2.  Run `python main.py` to test the worker locally.
