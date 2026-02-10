# Setup Guide - Burns Job Barometer

## Prerequisites

- Docker & Docker Compose
- Python 3.11+ (if running locally without Docker)
- Anthropic API Key (or OpenAI API Key)

## Quick Start (Docker)

1.  **Clone the repository**
    ```bash
    git clone <repo-url>
    cd BurnsJobBaramator
    ```

2.  **Configure Environment**
    Copy `.env.example` to `.env` and fill in your API keys.
    ```bash
    cp .env.example .env
    # Edit .env with your keys
    ```

3.  **Build and Run**
    ```bash
    docker-compose up --build
    ```

## Local Development (No Docker)

1.  **Create Virtual Environment**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Windows: .venv\Scripts\activate
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    playwright install chromium
    ```

3.  **Run Application**
    ```bash
    python main.py
    ```

## Project Structure

- `agents/`: Core logic for Scout, Barometer, Mirror, etc.
- `db/`: Database management and schema.
- `docs/`: Project documentation and specs.
- `storage/`: Generated outputs (resumes, logs).
- `utils/`: Helper functions.

## Configuration

Edit `config.yaml` to adjust:
- LLM provider and model
- Search keywords and locations
- Risk thresholds
- Scheduling intervals
