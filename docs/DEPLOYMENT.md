# Deployment Guide

## Architecture Overview

This system uses a **Worker + API** architecture to handle heavy processing while providing a lightweight interface.

1.  **The Worker:** Runs `main.py`. Scrapes jobs, analyzes fit, generates PDFs. Runs 24/7.
    *   *Supported Platforms:* Railway, Koyeb, Fly.io, Coolify (Self-Hosted).
2.  **The API (Vercel):** Runs `api/index.py`. Provides a lightweight endpoint to view job status.
3.  **The Database (Neon):** Central PostgreSQL database shared by both.

---

## 1. Database Setup (Neon)

1.  Create a project at [Neon.tech](https://neon.tech).
2.  Copy the **Connection String** (e.g., `postgresql://user:pass@...`).
3.  You will need this for all deployment targets.

---

## 2. The Worker (Choose One)

### Option A: Koyeb (Free Tier Available)
1.  **Sign up** at [Koyeb.com](https://koyeb.com).
2.  **Create App** -> **GitHub**.
3.  Select this repository.
4.  **Environment Variables:**
    *   `DATABASE_URL`: (Your Neon connection string)
    *   `ANTHROPIC_API_KEY`: (Your API key)
    *   `CLOUD_MODE`: `true` (This enables the 24/7 scheduler mode)
5.  **Deploy.** Koyeb will use `koyeb.yaml` or auto-detect the Dockerfile.

### Option B: Fly.io
1.  Install `flyctl`.
2.  Login: `fly auth login`.
3.  Launch: `fly launch` (It will detect `fly.toml`).
4.  Set Secrets:
    ```bash
    fly secrets set DATABASE_URL=... ANTHROPIC_API_KEY=...
    ```
5.  Deploy: `fly deploy`.

### Option C: Coolify (Self-Hosted)
1.  Install Coolify on your VPS.
2.  **Create Resource** -> **Application** -> **Public Repository**.
3.  Paste your GitHub URL.
4.  **Build Pack:** Select `Docker`.
5.  **Environment Variables:** Add `DATABASE_URL`, `ANTHROPIC_API_KEY`, and `CLOUD_MODE=true`.
6.  **Deploy.**

### Option D: Railway
1.  **Sign up** at [Railway.app](https://railway.app).
2.  **New Project** -> **Deploy from GitHub repo**.
3.  **Variables:** Add `DATABASE_URL`, `ANTHROPIC_API_KEY`, `CLOUD_MODE=true`.
4.  **Deploy.**

---

## 3. The API (Vercel)

**Purpose:** View job status remotely.

1.  **Sign up** at [Vercel.com](https://vercel.com).
2.  **Add New Project** -> Import from GitHub.
3.  **Environment Variables:**
    *   `DATABASE_URL`: (Same Neon connection string)
4.  **Deploy:** Vercel will build using `requirements-vercel.txt` (lightweight).

---

## 4. Local Development

1.  Create `.env` with your keys.
2.  Run `python main.py` to test the worker.
3.  Run `uvicorn api.index:app --reload` to test the API.
