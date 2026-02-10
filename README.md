# Burns Job Barometer

A persistent multi-agent system designed to find, filter, and apply for jobs automatically.

## 🚀 Features

- **The Scout:** Web scraper (DuckDuckGo + Playwright) to find jobs across the web (not just LinkedIn/Indeed).
- **The Barometer:** Analyzes job fit against your Strategic Narrative (0-100% score).
- **The Mirror:** Generates tailored resumes and cover letters using your Master Resume Source.
- **The Tribunal:** Multi-persona review system (ATS, Recruiter, Hiring Manager) to critique and refine applications.
- **The Gatekeeper:** Human-in-the-loop approval CLI to review and submit applications.

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
    # Edit .env with your ANTHROPIC_API_KEY
    ```

3.  **Install Dependencies**
    ```bash
    # Using uv (recommended)
    uv pip install -r requirements.txt
    playwright install chromium
    
    # Or standard pip
    pip install -r requirements.txt
    playwright install chromium
    ```

4.  **Run the System**
    ```bash
    python main.py
    ```

## 🐳 Docker Usage

```bash
docker-compose up --build
```

## 🧪 Testing

```bash
python -m pytest
```

## 📄 Documentation

See the `docs/` folder for detailed specifications and guides:
- `docs/BURNS_BAROMETER_SPEC.md`: System architecture and design.
- `docs/BURNS_MASTER_RESUME_SOURCE.md`: Source of truth for resume generation.
- `docs/02_COMPLETE_GUIDE.md`: Framework methodology.

##  License

MIT
