# 📦 Dependency Management - Flexible Versions Guide

**Purpose:** Never hardcode dependencies. Use flexible versions for development, locked versions for production.  
**Critical Rule:** NEVER use `==` in requirements.txt or pyproject.toml  
**Result:** No version conflicts, automatic security patches, easy updates

---

## 🚨 The Problem with Hardcoded Versions

### What Usually Happens (Wrong Way)

```txt
# requirements.txt - ❌ WRONG
pytest==7.4.3
fastapi==0.104.0
langchain==0.1.0
pydantic==2.5.0
sqlalchemy==2.0.23
```

**Problems this causes:**
- ❌ Gets outdated immediately
- ❌ Misses security patches
- ❌ Conflicts with other tools (pre-commit, IDE extensions)
- ❌ Breaks on different systems
- ❌ Can't use newer compatible versions
- ❌ Dependency hell when libraries update
- ❌ Forces old, potentially vulnerable versions

**Real Example:**
```bash
# You: "Install my requirements"
pip install -r requirements.txt

# Error: pytest==7.4.3 conflicts with 
# black>=23.0 which requires pytest>=7.0,<8.0
# Your linter: "I need pytest>=7.0"
# Your requirements: "No! Must be exactly 7.4.3!"
# Result: NOTHING WORKS
```

---

## ✅ The Solution: Flexible Versions

### The Right Way

```txt
# requirements.txt - ✅ CORRECT
pytest>=7.0
fastapi>=0.104
langchain>=0.1,<2.0
pydantic>=2.5
sqlalchemy>=2.0,<3.0
```

**Benefits:**
- ✅ Gets latest compatible versions automatically
- ✅ Security patches applied automatically
- ✅ No conflicts with other tools
- ✅ Works on different systems
- ✅ Future-proof (within compatibility bounds)
- ✅ Reproducible when needed (use lock file)

---

## 📘 Version Specifier Reference

### All Available Specifiers

```txt
>=   Minimum version                pytest>=7.0
>    Greater than                   pytest>6.0
<=   Maximum version                pytest<=8.0
<    Less than                      pytest<8.0
==   Exact version (avoid!)         pytest==7.4.3
~=   Compatible release             pytest~=7.4
!=   Exclude specific version       pytest!=7.4.2
,    Combine rules                  pytest>=7.0,<8.0
```

### When to Use Each

**`>=` - Most Common (Minimum Version)**
```txt
pytest>=7.0          # Get pytest 7.0 or newer
```
**Use for:** Most dependencies, especially test tools and utilities  
**Allows:** Any version 7.0+  
**Blocks:** Nothing (gets latest)

**`>=` with `<` - Recommended (Version Range)**
```txt
langchain>=0.1,<2.0  # Get 0.1.x or 1.x, not 2.0+
```
**Use for:** Libraries that break compatibility in major versions  
**Allows:** Minor and patch updates  
**Blocks:** Major breaking changes

**`~=` - Compatible Release**
```txt
pytest~=7.4          # Get 7.4.x but not 7.5+
```
**Use for:** When you need patch updates but not minor updates  
**Allows:** 7.4.0, 7.4.1, 7.4.2, etc  
**Blocks:** 7.5.0, 8.0.0, etc

**`!=` - Exclude Broken Version**
```txt
pytest!=7.4.2,>=7.0  # Any 7.x except broken 7.4.2
```
**Use for:** Skipping known broken releases  
**Allows:** All except specified  
**Blocks:** Specific broken version

**`==` - Exact Version (AVOID!)**
```txt
pytest==7.4.3        # Only exactly 7.4.3
```
**Use for:** NEVER in requirements.txt. Only in requirements-lock.txt  
**Allows:** Only exact version  
**Blocks:** Everything else

---

## 🎯 Version Strategies by Library Type

### Testing Tools (Get Latest Always)
```txt
# Always use >=
pytest>=7.0
pytest-asyncio>=0.21
pytest-cov>=4.0
pytest-mock>=3.0
black>=23.0
ruff>=0.0.100
mypy>=1.0
```
**Why:** Testing tools improve constantly, no reason to lock old versions

### LLM/Agent Libraries (Allow Minor, Block Major)
```txt
# Use >=X.Y,<MAJOR
langchain>=0.1,<2.0
langchain-openai>=0.0.5,<1.0
langchain-anthropic>=0.1,<2.0
langgraph>=0.0.5,<1.0
```
**Why:** Frequent improvements, but major versions break compatibility

### Core Libraries (Block Major Breaking)
```txt
# Use >=MAJOR.MINOR,<NEXT_MAJOR
fastapi>=0.104,<1.0
pydantic>=2.5,<3.0
sqlalchemy>=2.0,<3.0
```
**Why:** Major versions have breaking API changes

### Database Drivers (Stability Critical)
```txt
# Use >=X.Y,<NEXT_MAJOR
psycopg2-binary>=2.9,<3.0
pymongo>=4.0,<5.0
redis>=5.0,<6.0
```
**Why:** Database compatibility critical, breaking changes rare but serious

### Utilities (Less Critical)
```txt
# Use >=
python-dotenv>=1.0
pyyaml>=6.0
click>=8.0
```
**Why:** Stable APIs, breaking changes rare

---

## 📁 The 3-File System

### File 1: requirements.txt (Flexible - Development)

**Purpose:** Development and testing with latest compatible versions

```txt
# ================================================================================
# DEVELOPMENT REQUIREMENTS - FLEXIBLE VERSIONS ONLY
# ================================================================================
# Generated: February 4, 2026
# Usage: pip install -r requirements.txt
# 
# CRITICAL: This file uses FLEXIBLE versions (>=, ~=, <)
# NEVER use == in this file. For exact versions, see requirements-lock.txt
# ================================================================================

# Core Framework
fastapi>=0.104
uvicorn[standard]>=0.24
pydantic>=2.5,<3.0
python-dotenv>=1.0
pyyaml>=6.0

# LLM & Agents - Allow minor updates, block major breaking
langchain>=0.1,<2.0
langchain-openai>=0.0.5,<1.0
langchain-anthropic>=0.1,<2.0
langchain-google-genai>=0.0.5,<1.0
langgraph>=0.0.5,<1.0
langsmith>=0.0.70

# Database & Storage
sqlalchemy>=2.0,<3.0
psycopg2-binary>=2.9,<3.0
pgvector>=0.2
qdrant-client>=1.0,<2.0

# Cache
redis>=5.0,<6.0

# Security
cryptography>=41.0
python-jose>=3.3

# Monitoring & Observability
opentelemetry-api>=1.20
opentelemetry-sdk>=1.20
prometheus-client>=0.19

# Testing (always latest)
pytest>=7.0
pytest-asyncio>=0.21
pytest-cov>=4.0
pytest-mock>=3.0

# Code Quality (always latest)
black>=23.0
ruff>=0.0.100
mypy>=1.0

# ================================================================================
# USAGE INSTRUCTIONS:
# ================================================================================
# 
# DEVELOPMENT:
#   pip install -r requirements.txt
#   # Gets latest compatible versions
# 
# LOCK VERSIONS (after development):
#   pip freeze > requirements-lock.txt
#   # Creates exact versions for production
# 
# PRODUCTION:
#   pip install -r requirements-lock.txt
#   # Uses exact tested versions
# 
# UPDATE DEPENDENCIES:
#   pip install --upgrade -r requirements.txt
#   pytest  # Verify everything still works
#   pip freeze > requirements-lock.txt  # Update lock file
# ================================================================================
```

### File 2: requirements-lock.txt (Exact - Production)

**Purpose:** Production deployments with exact tested versions

```txt
# ================================================================================
# PRODUCTION REQUIREMENTS - EXACT LOCKED VERSIONS
# ================================================================================
# Generated: February 4, 2026
# Created by: pip freeze > requirements-lock.txt
# 
# CRITICAL: This file contains EXACT versions (==) for reproducible deployments
# DO NOT edit manually. Regenerate by running: pip freeze > requirements-lock.txt
# ================================================================================

annotated-types==0.6.0
anyio==4.2.0
black==23.12.1
certifi==2023.11.17
charset-normalizer==3.3.2
click==8.1.7
cryptography==41.0.7
dataclasses-json==0.6.3
fastapi==0.104.1
h11==0.14.0
httpcore==1.0.2
httpx==0.26.0
idna==3.6
langchain==0.1.0
langchain-anthropic==0.1.1
langchain-core==0.1.10
langchain-google-genai==0.0.5
langchain-openai==0.0.5
langsmith==0.0.77
mypy==1.8.0
openai==1.6.1
opentelemetry-api==1.22.0
opentelemetry-sdk==1.22.0
pgvector==0.2.4
prometheus-client==0.19.0
psycopg2-binary==2.9.9
pydantic==2.5.3
pydantic-core==2.14.6
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-mock==3.12.0
python-dotenv==1.0.0
python-jose==3.3.0
pyyaml==6.0.1
qdrant-client==1.7.0
redis==5.0.1
requests==2.31.0
ruff==0.1.9
sniffio==1.3.0
sqlalchemy==2.0.25
typing-extensions==4.9.0
urllib3==2.1.0
uvicorn==0.24.0.post1

# ================================================================================
# USAGE INSTRUCTIONS:
# ================================================================================
# 
# PRODUCTION DEPLOYMENT:
#   pip install -r requirements-lock.txt
#   # Uses exact versions tested in development
# 
# DOCKER:
#   COPY requirements-lock.txt .
#   RUN pip install -r requirements-lock.txt
# 
# UPDATING:
#   # In development:
#   pip install --upgrade -r requirements.txt
#   pytest  # Verify
#   pip freeze > requirements-lock.txt
#   # Commit new lock file
# ================================================================================
```

### File 3: pyproject.toml (Flexible - Distribution)

**Purpose:** Package metadata and flexible dependencies for distribution

```toml
[project]
name = "ai-agent-system"
version = "0.1.0"
description = "Secure, scalable AI agent system with flexible architecture"
readme = "README.md"
requires-python = ">=3.11"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
keywords = ["ai", "agents", "langchain", "llm"]

# ================================================================================
# MAIN DEPENDENCIES - FLEXIBLE VERSIONS
# ================================================================================
# CRITICAL: Use flexible versions here (>=, ~=, <) NOT exact versions (==)
# This allows users of your package to install with their preferred versions
# ================================================================================

dependencies = [
    # Core
    "fastapi>=0.104",
    "uvicorn[standard]>=0.24",
    "pydantic>=2.5,<3.0",
    "python-dotenv>=1.0",
    "pyyaml>=6.0",
    
    # LLM & Agents
    "langchain>=0.1,<2.0",
    "langchain-openai>=0.0.5,<1.0",
    "langchain-anthropic>=0.1,<2.0",
    "langchain-google-genai>=0.0.5,<1.0",
    "langgraph>=0.0.5,<1.0",
    "langsmith>=0.0.70",
    
    # Database
    "sqlalchemy>=2.0,<3.0",
    "psycopg2-binary>=2.9,<3.0",
    "pgvector>=0.2",
    "qdrant-client>=1.0,<2.0",
    
    # Cache
    "redis>=5.0,<6.0",
    
    # Security
    "cryptography>=41.0",
    "python-jose>=3.3",
    
    # Monitoring
    "opentelemetry-api>=1.20",
    "opentelemetry-sdk>=1.20",
    "prometheus-client>=0.19",
]

[project.optional-dependencies]
# Development dependencies (always get latest)
dev = [
    "pytest>=7.0",
    "pytest-asyncio>=0.21",
    "pytest-cov>=4.0",
    "pytest-mock>=3.0",
    "black>=23.0",
    "ruff>=0.0.100",
    "mypy>=1.0",
]

# Evaluation tools
eval = [
    "deepeval>=0.20",
    "ragas>=0.1",
]

# Monitoring tools
monitoring = [
    "datadog>=0.46.0",
    "sentry-sdk>=1.30.0",
]

[project.urls]
Homepage = "https://github.com/yourusername/ai-agent-system"
Documentation = "https://docs.example.com"
Repository = "https://github.com/yourusername/ai-agent-system"
Issues = "https://github.com/yourusername/ai-agent-system/issues"

[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--cov=app",
    "--cov-report=term-missing",
    "--cov-report=html",
]

[tool.black]
line-length = 100
target-version = ['py311']

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

---

## 🔄 Complete Workflow

### Step 1: Initial Setup (First Time)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install with flexible versions
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
pytest
```

### Step 2: Development (Daily Work)

```bash
# Activate environment
source venv/bin/activate

# Install any new dependencies (flexible versions)
pip install -r requirements.txt

# Work on your code
# ...

# Run tests frequently
pytest
```

### Step 3: Lock Versions (Before Committing)

```bash
# After adding new dependencies or updating
pip install --upgrade -r requirements.txt

# Run full test suite
pytest

# If tests pass, lock versions
pip freeze > requirements-lock.txt

# Commit BOTH files
git add requirements.txt requirements-lock.txt
git commit -m "Update dependencies"
```

### Step 4: Production Deployment

```bash
# Use locked versions for reproducibility
pip install -r requirements-lock.txt

# Or in Docker:
# COPY requirements-lock.txt .
# RUN pip install -r requirements-lock.txt
```

### Step 5: Update Dependencies (Monthly)

```bash
# Check for updates
pip list --outdated

# Update to latest compatible
pip install --upgrade -r requirements.txt

# Test thoroughly
pytest
pytest -v --cov=app  # Check coverage
pytest tests/integration/  # Integration tests
pytest tests/security/  # Security tests

# If all pass, update lock file
pip freeze > requirements-lock.txt

# Commit
git add requirements.txt requirements-lock.txt
git commit -m "Monthly dependency update - all tests pass"
```

---

## 🐳 Docker Integration

### Dockerfile (Using Lock File)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY requirements-lock.txt .

# Install exact versions for production
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-lock.txt

# Copy application
COPY . .

# Run
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Multi-Stage Docker (Development + Production)

```dockerfile
# ============================================================================
# Stage 1: Development (uses flexible versions)
# ============================================================================
FROM python:3.11-slim AS development

WORKDIR /app

RUN apt-get update && apt-get install -y gcc postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Use flexible versions for development
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ============================================================================
# Stage 2: Production (uses locked versions)
# ============================================================================
FROM python:3.11-slim AS production

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Use locked versions for production
COPY requirements-lock.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-lock.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  # Development service (flexible versions)
  app-dev:
    build:
      context: .
      target: development
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - ENV=development
    env_file:
      - .env
    depends_on:
      - db
      - redis

  # Production service (locked versions)
  app-prod:
    build:
      context: .
      target: production
    ports:
      - "8000:8000"
    environment:
      - ENV=production
    env_file:
      - .env.production
    depends_on:
      - db
      - redis

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: agentdb
      POSTGRES_USER: agent
      POSTGRES_PASSWORD: secret
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

---

## 🚨 Common Mistakes & How to Avoid

### Mistake 1: Using == in requirements.txt

**Wrong:**
```txt
pytest==7.4.3
```

**Right:**
```txt
pytest>=7.0
```

**Why:** Gets latest security patches automatically

### Mistake 2: Forgetting to Create Lock File

**Wrong:**
```bash
pip install -r requirements.txt
# Deploy to production
```

**Right:**
```bash
pip install -r requirements.txt
pytest  # Test
pip freeze > requirements-lock.txt  # Lock versions
# Deploy with requirements-lock.txt
```

**Why:** Production needs reproducible builds

### Mistake 3: Editing Lock File Manually

**Wrong:**
```txt
# requirements-lock.txt
# Manually change version
pytest==7.4.3  # Changed to 7.4.4
```

**Right:**
```bash
pip install --upgrade pytest
pytest  # Test
pip freeze > requirements-lock.txt  # Regenerate
```

**Why:** Lock file should always match installed packages

### Mistake 4: Not Testing After Updates

**Wrong:**
```bash
pip install --upgrade -r requirements.txt
pip freeze > requirements-lock.txt
git commit -m "Update deps"  # Without testing!
```

**Right:**
```bash
pip install --upgrade -r requirements.txt
pytest  # Run full test suite
pytest -v --cov  # Check coverage
pytest tests/integration/  # Integration tests
# Only if ALL pass:
pip freeze > requirements-lock.txt
git commit -m "Update deps - all tests pass"
```

**Why:** Updates can break things

### Mistake 5: Using Flexible Versions in Docker Production

**Wrong:**
```dockerfile
# Dockerfile
COPY requirements.txt .
RUN pip install -r requirements.txt  # Flexible versions!
```

**Right:**
```dockerfile
# Dockerfile
COPY requirements-lock.txt .
RUN pip install -r requirements-lock.txt  # Exact versions
```

**Why:** Production must be reproducible

---

## 🎯 Version Strategy Quick Reference

| Library Type | Strategy | Example | Why |
|--------------|----------|---------|-----|
| Testing Tools | `>=X.0` | `pytest>=7.0` | Always get latest improvements |
| LLM Libraries | `>=X.Y,<MAJOR` | `langchain>=0.1,<2.0` | Allow updates, block breaking |
| Core Frameworks | `>=X.Y,<MAJOR` | `fastapi>=0.104,<1.0` | Stability important |
| Database Drivers | `>=X.Y,<MAJOR` | `psycopg2-binary>=2.9,<3.0` | Breaking changes serious |
| Utilities | `>=X.0` | `pyyaml>=6.0` | Stable, low risk |
| Known Broken | `!=X.Y.Z,>=X.0` | `pytest!=7.4.2,>=7.0` | Skip specific bad version |

---

## 📋 Integration with Claude Code/Cursor

### Tell Your AI Assistant

```markdown
BEFORE YOU GENERATE ANY DEPENDENCY FILES:

RULE 1: NEVER use == in requirements.txt or pyproject.toml
RULE 2: ALWAYS use flexible versions: >=, ~=, <
RULE 3: ALWAYS create THREE files:
        - requirements.txt (flexible)
        - requirements-lock.txt (exact, from pip freeze)
        - pyproject.toml (flexible)

Testing tools:     pytest>=7.0
LLM libraries:     langchain>=0.1,<2.0
Core frameworks:   fastapi>=0.104,<1.0
Database drivers:  psycopg2-binary>=2.9,<3.0
Utilities:         python-dotenv>=1.0

After installing:
1. Run: pip freeze > requirements-lock.txt
2. Test: pytest
3. Commit BOTH requirements.txt and requirements-lock.txt
```

### Add to .claude-context.md

```markdown
## Dependency Management

### Current Strategy
- Development: requirements.txt (flexible versions >=, <)
- Production: requirements-lock.txt (exact versions ==)
- Distribution: pyproject.toml (flexible versions)

### Key Rules
- NEVER use == in requirements.txt
- ALWAYS lock versions before deployment
- ALWAYS test after updates
- UPDATE monthly, lock after testing

### Current Versions (Locked)
Last updated: [DATE]
Last tested: [DATE]
Lock file: requirements-lock.txt

See: docs/03_DEPENDENCY_MANAGEMENT.md for complete guide
```

---

## ✅ Checklist Before Completing Project

### File Checklist
- [ ] requirements.txt uses flexible versions (>=, ~=, <)
- [ ] requirements-lock.txt generated with `pip freeze`
- [ ] pyproject.toml uses flexible versions
- [ ] All three files committed to git
- [ ] .env.example documents which packages need API keys

### Testing Checklist
- [ ] All tests pass with flexible versions
- [ ] All tests pass with locked versions
- [ ] Coverage >80%
- [ ] Integration tests pass
- [ ] Security tests pass

### Documentation Checklist
- [ ] .claude-context.md mentions dependency strategy
- [ ] README.md has installation instructions
- [ ] SETUP.md explains 3-file system
- [ ] Requirements documented

### Deployment Checklist
- [ ] Dockerfile uses requirements-lock.txt
- [ ] docker-compose.yml configured correctly
- [ ] Production uses locked versions
- [ ] Rollback plan includes dependency versions

---

## 📊 Expected Results

### Development Experience
✅ No version conflicts  
✅ Latest security patches automatically  
✅ Tools work without configuration  
✅ Fast iteration  

### Production Experience
✅ Reproducible builds  
✅ Predictable behavior  
✅ No surprise updates  
✅ Easy rollback  

### Maintenance Experience
✅ Easy updates (monthly)  
✅ Clear testing process  
✅ Low conflict resolution  
✅ Future-proof architecture  

---

## 🎓 Advanced Topics

### Handling Conflicting Dependencies

**Problem:**
```
Package A requires: package-x>=1.0,<2.0
Package B requires: package-x>=2.0
```

**Solution:**
```bash
# Check for conflicts
pip check

# Use pip-compile from pip-tools
pip install pip-tools
pip-compile requirements.in --resolver=backtracking

# Or manually adjust versions
```

### Using pip-tools (Advanced)

```bash
# Install pip-tools
pip install pip-tools

# Create requirements.in (high-level deps)
echo "fastapi>=0.104" > requirements.in
echo "pytest>=7.0" >> requirements.in

# Compile to requirements.txt
pip-compile requirements.in

# Sync environment
pip-sync requirements.txt
```

### Poetry Alternative

```toml
# pyproject.toml
[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104"
langchain = "^0.1"

[tool.poetry.dev-dependencies]
pytest = "^7.0"
black = "^23.0"
```

```bash
poetry install
poetry lock
poetry export -f requirements.txt > requirements-lock.txt
```

---

## 🔗 References

- **Quick Reference:** 01_QUICK_REFERENCE.md (Dependency section)
- **Complete Guide:** 02_COMPLETE_GUIDE.md (File setup)
- **Start Here:** 00_START_HERE.md (Navigation)
- **PEP 440:** https://peps.python.org/pep-0440/ (Version specifiers)
- **pip User Guide:** https://pip.pypa.io/en/stable/user_guide/

---

**Remember: Flexible in development, locked in production!** 📦

*Version 1.0.0 | Last Updated: February 2026*
