# Burns Job Barometer

A persistent multi-agent system designed to find, filter, and apply for jobs automatically.

## 🚀 Features

- **The Scout:** Web scraper (DuckDuckGo + Playwright) to find jobs across the web.
- **The Barometer:** Analyzes job fit against your Strategic Narrative (0-100% score).
- **The Mirror:** Generates tailored resumes and cover letters.
- **The Tribunal:** Multi-persona review system to critique applications.
- **The Gatekeeper:** Human-in-the-loop approval CLI.

## 🛠️ Setup

1.  **Clone the repository**
    ```bash
    git clone <repo-url>
    cd BurnsJobBaramator
    ```

2.  **Configure Environment**
    Copy `.env.example` to `.env` and fill in your API keys.
    ```bash
    cp .env.example .env
    ```

3.  **Install Dependencies**
    ```bash
    # Using uv (recommended)
    uv pip install -r requirements.txt
    playwright install chromium
    ```

4.  **Run the System**
    ```bash
    python main.py
    ```

## ☁️ Deployment

Deploy the worker to **Railway** or **Fly.io**.

See `docs/DEPLOYMENT.md` for full instructions.

## 🐳 Docker Usage

```bash
docker-compose up --build
```

## 🧪 Testing

```bash
python -m pytest
```

##  License

MIT
