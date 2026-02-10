# 🎯 Quick Reference - AI Agent Development Framework

**Read this first. Everything else is details.**

---

## ⚡ Super Quick Start (5 min)

```bash
1. Put all docs in /docs folder
2. Tell AI: "Read /docs before building"
3. Follow 7-step process below
4. Build!
```

---

## 🎯 The 7-Step Process (Use for EVERY Project)

```
Step 1: DISCOVERY
├─ What problem are we solving?
├─ Who uses it? How?
└─ What does success look like?

Step 2: RISK SCORING
├─ Input risk (0-5): How dangerous is user input?
├─ Output risk (0-5): What could wrong outputs cause?
├─ Data sensitivity (0-4): PII? Financial? Medical?
└─ TOTAL = Input + Output + Data

Step 3: GUARDRAILS (Auto-enabled based on risk)
├─ 0-4 (LOW): Basic validation, logging
├─ 5-10 (MEDIUM): + content filtering, rate limiting
└─ 11+ (HIGH): + human approval, audit logging, encryption

Step 4: ARCHITECTURE
├─ Simple (MVP, <1K users): Monolith
├─ Medium (Production, <10K users): Modular monolith
└─ Complex (Scale, 10K+ users): Microservices

Step 5: REVIEW GATE
├─ Check all checklists
├─ Approve architecture
└─ Proceed to build

Step 6: IMPLEMENTATION
├─ Phase 1: Core features + tests
├─ Phase 2: Integration + security tests
└─ Phase 3: Optimization + monitoring

Step 7: DEPLOY & MONITOR
├─ Deploy with monitoring
├─ Track metrics
└─ Iterate based on data
```

---

## 📊 Risk Scoring Formula

```
RISK SCORE = Input Risk + Output Risk + Data Sensitivity

Input Risk (0-5):
0 = None
1 = Low (preset options)
2 = Medium (structured text)
3 = High (free-form text)
4 = Very High (code/commands)
5 = Extreme (direct DB/API)

Output Risk (0-5):
0 = None (read-only)
1 = Low (informational)
2 = Medium (recommendations)
3 = High (decisions)
4 = Very High (automated actions)
5 = Extreme (financial/medical)

Data Sensitivity (0-4):
0 = None (public data)
1 = Low (non-sensitive)
2 = Medium (business data)
3 = High (PII)
4 = Extreme (medical/financial)

TOTAL RISK:
0-4:   LOW      → Basic guardrails
5-10:  MEDIUM   → Standard guardrails
11+:   HIGH     → Comprehensive guardrails
```

---

## 🛡️ Auto-Enabled Guardrails by Risk

### LOW Risk (0-4)
```
✓ Input validation (basic)
✓ Output validation (basic)
✓ Logging
✓ Error handling
```

### MEDIUM Risk (5-10)
```
✓ Everything from LOW, plus:
✓ Prompt injection detection
✓ Content filtering
✓ Rate limiting
✓ PII redaction (basic)
```

### HIGH Risk (11+)
```
✓ Everything from MEDIUM, plus:
✓ Human approval for critical actions
✓ Comprehensive audit logging
✓ Encryption (at rest + in transit)
✓ Multi-factor verification
✓ Rollback capabilities
```

---

## 🔄 Easy Swapping (No Rewrites!)

### Swap LLM Models (1 line change)
```python
# config/llm.py
llm = ChatOpenAI(model="gpt-4")              # OpenAI
llm = ChatAnthropic(model="claude-3-opus")   # Claude
llm = ChatGoogle(model="gemini-pro")         # Google

# Rest of code: IDENTICAL
```

### Swap Databases (1 env var)
```bash
# .env
DATABASE_TYPE=postgresql    # PostgreSQL
DATABASE_TYPE=qdrant        # Qdrant

# Code: IDENTICAL - uses adapter pattern
```

### Add LLMs to Debate (config only)
```yaml
# config/multi_llm.yaml
agents:
  optimist:
    llm_provider: openai
    model: gpt-4
  skeptic:
    llm_provider: claude
    model: claude-3-opus
  analyst:
    llm_provider: google
    model: gemini-pro

# No code changes required!
```

---

## 📁 Required Files (Generate these FIRST)

```
.gitignore
.dockerignore
.env.example               ← Include API key setup links!
README.md
SETUP.md
ARCHITECTURE.md
DEPLOYMENT.md
docker-compose.yml
Dockerfile
requirements.txt           ← FLEXIBLE versions (>=, not ==)
requirements-lock.txt      ← Exact versions (from pip freeze)
pyproject.toml
pytest.ini
.pre-commit-config.yaml
.claude-context.md         ← CRITICAL - Claude's project memory
.bugs_tracker.md           ← CRITICAL - Bug tracking & prevention
```

---

## 🚨 CRITICAL: Claude Context & Bug Files

### .claude-context.md (Update after EVERY build)
```markdown
# Project Context for Claude

## Current State
- Last updated: [DATE]
- Current phase: [Phase X]
- Working on: [Feature/Task]

## Recent Changes
- [What changed in last session]
- [New files created]
- [APIs modified]

## Project Structure
```
/app
  /agents      - Agent implementations
  /tools       - Tool integrations
  /db          - Database adapters
  /guardrails  - Security patterns
```

## Known Issues
- [Issue 1]
- [Issue 2]

## Next Steps
- [ ] Task 1
- [ ] Task 2

## Important Notes
- [Critical decisions made]
- [Patterns being used]
- [Dependencies to watch]
```

### .bugs_tracker.md (Update when bugs found)
```markdown
# Bug Tracker

## Active Bugs
### BUG-001: [Description]
- Status: Active
- Severity: High/Medium/Low
- Found: [DATE]
- File: [FILE PATH]
- Reproduce: [Steps]
- Fix attempted: [What was tried]
- Blocked by: [Dependencies]

## Resolved Bugs
### BUG-XXX: [Description]
- Status: Resolved
- Fixed: [DATE]
- Solution: [What worked]

## Known Limitations
- [Limitation 1]
- [Limitation 2]
```

---

## ⚙️ Dependency Management (NEVER use ==)

### ❌ WRONG (Hardcoded versions)
```txt
pytest==7.4.3
fastapi==0.104.0
langchain==0.1.0
```

### ✅ CORRECT (Flexible versions)
```txt
pytest>=7.0
fastapi>=0.104
langchain>=0.1,<2.0
```

### The 3-File System
```bash
requirements.txt         # Flexible (development)
requirements-lock.txt    # Exact (production)
pyproject.toml          # Flexible (distribution)
```

### Workflow
```bash
# Development
pip install -r requirements.txt

# Lock versions
pip freeze > requirements-lock.txt

# Production
pip install -r requirements-lock.txt
```

---

## 🧪 Testing Requirements

```
Unit Tests:        60-70%  (isolated, all mocked)
Integration Tests: 20-30%  (real components, mocked externals)
E2E Tests:         5-10%   (everything real)

TARGET: 80%+ coverage

MUST INCLUDE:
✓ Security tests (injection, auth)
✓ Integration tests (components work together)
✓ Permission tests (who can do what)
✓ Edge case tests (nulls, empty, errors)
```

---

## 📋 Pre-Build Checklist

Before writing ANY code:

- [ ] Completed discovery (Step 1)
- [ ] Calculated risk score (Step 2)
- [ ] Identified required guardrails (Step 3)
- [ ] Chosen architecture (Step 4)
- [ ] Passed review gate (Step 5)
- [ ] Generated all required files
- [ ] Setup .claude-context.md
- [ ] Setup .bugs_tracker.md
- [ ] AI knows to read /docs folder

---

## 📋 Pre-Deployment Checklist

Before going to production:

- [ ] 80%+ test coverage
- [ ] All security tests passing
- [ ] Code reviewed
- [ ] Documentation complete
- [ ] Monitoring configured
- [ ] .claude-context.md up to date
- [ ] .bugs_tracker.md up to date
- [ ] Rollback plan ready
- [ ] Performance tested
- [ ] Load tested

---

## 🎯 Architecture Decision Tree

```
How many users?
├─ < 1,000 users
│  └─ Start with: MONOLITH (single app, easy to manage)
├─ 1K-10K users
│  └─ Use: MODULAR MONOLITH (organized, can split later)
└─ 10K+ users
   └─ Consider: MICROSERVICES (scale independently)

How complex is the workflow?
├─ Single agent, simple task
│  └─ Pattern: SIMPLE AGENT (direct LLM call)
├─ Multiple steps, sequential
│  └─ Pattern: PIPELINE (step 1 → step 2 → step 3)
└─ Multiple agents, collaborate
   └─ Pattern: MULTI-AGENT (agents communicate)

How much autonomy?
├─ Read-only or recommendations
│  └─ Guardrails: LOW (basic validation)
├─ Makes decisions, awaits approval
│  └─ Guardrails: MEDIUM (human approval)
└─ Takes actions automatically
   └─ Guardrails: HIGH (comprehensive, audit)
```

---

## 💡 Common Patterns

### Database Adapter Pattern
```python
# app/db/adapter.py
class DatabaseAdapter:
    def save(self, data): pass
    def load(self, id): pass
    def search(self, query): pass

class PostgreSQLAdapter(DatabaseAdapter):
    # PostgreSQL implementation

class QdrantAdapter(DatabaseAdapter):
    # Qdrant implementation

# app/db/__init__.py
def get_database():
    db_type = os.getenv("DATABASE_TYPE", "postgresql")
    if db_type == "postgresql":
        return PostgreSQLAdapter()
    elif db_type == "qdrant":
        return QdrantAdapter()

# Usage (same everywhere)
db = get_database()
db.save(data)  # Works with any database!
```

### Multi-LLM Debate Pattern
```yaml
# config/debate.yaml
debate_type: consensus  # or pros_cons, voting

agents:
  - name: optimist
    llm_provider: openai
    model: gpt-4
    role: "Focus on opportunities and positive outcomes"
    
  - name: skeptic
    llm_provider: claude
    model: claude-3-opus
    role: "Identify risks and potential problems"
    
  - name: analyst
    llm_provider: google
    model: gemini-pro
    role: "Provide balanced, data-driven analysis"

rounds: 2
consensus_threshold: 0.7
```

---

## 🔍 Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| Version conflicts | Use flexible versions (>=, not ==) |
| Claude losing context | Update .claude-context.md |
| Repetitive bugs | Use .bugs_tracker.md |
| Architecture unclear | Calculate risk, use decision tree |
| Security gaps | Enable guardrails based on risk |
| Tests failing | Check .claude-context.md for known issues |
| Deployment errors | Verify all checklist items |
| AI not helping well | Update system prompt (see 04_AI_ASSISTANT_INTEGRATION.md) |

---

## 📞 Where to Find More Info

| Topic | File |
|-------|------|
| Complete methodology | 02_COMPLETE_GUIDE.md |
| Dependency management | 03_DEPENDENCY_MANAGEMENT.md |
| AI assistant setup | 04_AI_ASSISTANT_INTEGRATION.md |
| Claude context & bugs | 05_CLAUDE_CONTEXT_AND_BUGS.md |
| Navigation & overview | 00_START_HERE.md |

---

## ⚡ Daily Workflow

### Morning
```bash
# Check what changed
cat .claude-context.md | tail -20

# Check active bugs
grep "Status: Active" .bugs_tracker.md

# Plan work based on context
```

### During Build
```bash
# Quick reference (this file)
less docs/01_QUICK_REFERENCE.md

# Detailed patterns
less docs/02_COMPLETE_GUIDE.md
```

### End of Day
```bash
# Update context
vim .claude-context.md
# Add: what changed, what's next, any blockers

# Update bugs
vim .bugs_tracker.md  
# Add: new bugs found, progress on existing

# Commit
git add .claude-context.md .bugs_tracker.md
git commit -m "EOD: context and bugs update"
```

---

## 🎓 Expected Benefits

### After 1st Project
- ✅ Understand 7-step process
- ✅ Know what questions to ask
- ✅ Have production-ready structure

### After 3rd Project
- ✅ 30% faster development
- ✅ Zero security oversights
- ✅ 60%+ code reuse

### After 5th Project
- ✅ 50% faster development
- ✅ 80%+ code reuse
- ✅ Build production systems in days
- ✅ Patterns become automatic

---

## 🎯 Core Principles

1. **Discovery First** - Ask before building
2. **Risk-Based Security** - Match security to actual risk
3. **Easy Swapping** - Never lock into one vendor/tech
4. **Context Preservation** - Claude context & bugs files critical
5. **Flexible Dependencies** - Never hardcode versions
6. **Test-Driven** - 80%+ coverage from start
7. **Production-Ready Day 1** - All pieces in place

---

## 📊 By The Numbers

- **7** steps in every project
- **15** required files to generate
- **2** critical files to update daily (.claude-context.md, .bugs_tracker.md)
- **3** dependency files (requirements, lock, pyproject)
- **80%+** test coverage target
- **30-50%** faster after 3-4 projects
- **100%** security gaps prevented (via checklists)

---

## 🚀 Your Next Action

**Pick ONE:**

1. **Start new project** → Follow 7-step process above
2. **Fix current issue** → Check troubleshooting table
3. **Learn patterns** → Read 02_COMPLETE_GUIDE.md
4. **Setup AI assistant** → Read 04_AI_ASSISTANT_INTEGRATION.md

---

## ✅ Success Indicators

You're using this right when:

✅ Every project starts with 7-step process  
✅ Risk scores calculated before architecture  
✅ .claude-context.md updated after every session  
✅ .bugs_tracker.md tracks all issues  
✅ No hardcoded dependency versions  
✅ Can swap LLMs/databases without rewrites  
✅ 80%+ test coverage from day 1  
✅ Production-ready on first deployment  

---

**Save this. Reference it daily. Build amazing systems!** 🚀

*Version 1.0.0 | Last Updated: February 2026*
