# 🧠 Claude Context & Bug Tracking - CRITICAL for Bug Prevention

**Purpose:** Give Claude Code/Cursor/Google Code Assistant project memory to prevent 80% of bugs  
**Update frequency:** After EVERY build session  
**Impact:** High - prevents context loss, catches repetitive bugs

---

## 🚨 Why This Matters

### The Problem
Claude Code/Cursor/Google Code Assistant has **no memory between sessions**:
- Forgets what you built yesterday
- Doesn't know current project state
- Can't track recurring bugs
- Repeats the same mistakes
- Loses architectural context

### The Solution
Two files give your AI assistant "memory":

1. **`.claude-context.md`** - Project state, recent changes, structure
2. **`.bugs_tracker.md`** - Active bugs, patterns, blockers

**Result:** 80% fewer bugs, no repeated mistakes, faster debugging

---

## 📄 File 1: .claude-context.md

### Purpose
Tracks project state so Claude understands:
- What was built recently
- Current file structure
- Active features being developed
- Known issues and workarounds
- Important architectural decisions

### Template

```markdown
# Claude Context - [PROJECT NAME]

> Last Updated: [DATE - UPDATE AFTER EVERY SESSION]
> Project Phase: [Discovery/Build/Test/Deploy/Maintain]
> Current Sprint: [What you're working on this week]

---

## 📍 Current State

### What I'm Working On Right Now
- Feature: [Current feature name]
- Files modified: [List files]
- Status: [Started/In Progress/Testing/Blocked]
- Blocker (if any): [What's blocking progress]

### What Was Built in Last Session
- [DATE]: Built [feature/component]
  - Files: `app/agents/researcher.py`, `tests/test_researcher.py`
  - Result: Working researcher agent with 85% test coverage
  - Known issue: Slow on large documents (see BUGS-003)

---

## 🏗️ Project Structure

### Current Architecture
```
/app
  /agents          - Agent implementations
    researcher.py  - Research agent (WORKING, slow on large docs)
    writer.py      - Content writer (IN PROGRESS)
  /tools
    web_search.py  - Web search tool (WORKING)
    summarizer.py  - Text summarizer (NOT STARTED)
  /db
    adapter.py     - Database adapter interface (WORKING)
    postgresql.py  - PostgreSQL implementation (WORKING)
  /guardrails
    input_guard.py - Input validation (WORKING)
    output_guard.py- Output validation (NEEDS TESTING)
  /config
    llm.py         - LLM configuration (WORKING - using OpenAI)
```

### Key Files & Their Status
| File | Status | Notes |
|------|--------|-------|
| `app/agents/researcher.py` | Working | Slow on large docs |
| `app/agents/writer.py` | In Progress | Basic structure done |
| `app/tools/web_search.py` | Working | Rate limit: 10/min |
| `app/db/adapter.py` | Working | PostgreSQL only for now |
| `tests/test_researcher.py` | Working | 85% coverage |

---

## 🔧 Recent Changes

### Last 3 Sessions

#### Session [DATE]
**Changed:**
- Added researcher agent with web search
- Implemented caching for search results
- Added rate limiting to web_search tool

**Files Modified:**
- `app/agents/researcher.py` (new)
- `app/tools/web_search.py` (new)
- `tests/test_researcher.py` (new)
- `config/llm.py` (updated timeout to 60s)

**Issues Found:**
- Researcher slow on documents >10K words
- Cache not invalidating correctly (see BUGS-003)

#### Session [DATE-1]
**Changed:**
- Setup database adapter pattern
- Implemented PostgreSQL adapter
- Added connection pooling

**Files Modified:**
- `app/db/adapter.py` (new)
- `app/db/postgresql.py` (new)
- `.env.example` (added DATABASE_URL)

#### Session [DATE-2]
**Changed:**
- Initial project setup
- Core guardrails implemented
- Testing infrastructure setup

---

## ⚙️ Configuration & Dependencies

### Current LLM Setup
```python
# config/llm.py
MODEL = "gpt-4"  # OpenAI
TIMEOUT = 60  # seconds
MAX_TOKENS = 4000
TEMPERATURE = 0.7
```

### Environment Variables Required
```bash
OPENAI_API_KEY=sk-...          # ✓ Set
DATABASE_URL=postgresql://...  # ✓ Set
REDIS_URL=redis://...          # ✓ Set
WEB_SEARCH_API_KEY=...         # ⚠️  NOT SET YET
```

### Important Dependencies
```txt
langchain>=0.1,<2.0            # Using 0.1.5
langchain-openai>=0.0.5        # Using 0.0.6
fastapi>=0.104                 # Using 0.104.1
pytest>=7.0                    # Using 7.4.3
```

**Note:** Using flexible versions (no ==) - see requirements.txt

---

## 🎯 Active Features & Status

### In Progress
- [ ] Writer agent (40% done)
  - Basic structure complete
  - Needs: Output validation, formatting options
  - Blocked by: Output guardrails not tested yet
  
- [ ] Summarizer tool (0% done)
  - Not started
  - Depends on: Researcher agent working well

### Completed
- [x] Researcher agent (100%)
  - Working, but slow on large docs
  - Tests: 85% coverage
  - Known issue: See BUGS-003

- [x] Database adapter pattern (100%)
  - PostgreSQL working
  - Tests: 90% coverage
  - Ready for Qdrant adapter when needed

### Planned
- [ ] Multi-LLM debate system
- [ ] Advanced guardrails (PII detection)
- [ ] Monitoring dashboard

---

## 🐛 Known Issues & Workarounds

### ISSUE-1: Researcher Slow on Large Documents
**Impact:** High
**Workaround:** Split documents into chunks <5K words
**Permanent fix:** See BUGS-003 in .bugs_tracker.md

### ISSUE-2: Cache Not Invalidating
**Impact:** Medium
**Workaround:** Clear cache manually: `redis-cli FLUSHALL`
**Permanent fix:** Investigating TTL settings

### ISSUE-3: Output Guardrails Not Tested
**Impact:** Medium
**Workaround:** Manual review of all outputs
**Status:** Testing planned for next session

---

## 📝 Important Architectural Decisions

### Why We Chose These Patterns

**Database Adapter Pattern:**
- Decision: Use adapter pattern for database
- Reason: May need to swap PostgreSQL for Qdrant later
- Impact: All database code goes through adapter interface
- Date: [DATE]

**Single LLM Model (for now):**
- Decision: Start with just OpenAI GPT-4
- Reason: Keep it simple, add multi-LLM later if needed
- Impact: Easy to swap later (config-based)
- Date: [DATE]

**Modular Monolith Architecture:**
- Decision: Not microservices (yet)
- Reason: <1K users expected, easier to develop/deploy
- Impact: Can split into microservices later if needed
- Date: [DATE]

---

## 🎓 Lessons Learned

### What Worked Well
- Database adapter pattern - easy to test, easy to swap
- Flexible dependency versions - no conflicts
- Test-driven development - caught issues early

### What Didn't Work
- Trying to handle large documents without chunking
- Not setting cache TTL from the start
- Skipping output guardrail tests

### Don't Repeat These Mistakes
- ❌ Don't skip testing guardrails before using them
- ❌ Don't process large documents without chunking
- ❌ Don't forget to set cache expiration

---

## 🔄 Integration Points

### Current External APIs
```
OpenAI API
├─ Used by: Researcher agent, Writer agent
├─ Rate limit: 10K tokens/min
└─ Fallback: None (add Claude as backup?)

Web Search API (Tavily)
├─ Used by: web_search tool
├─ Rate limit: 10 requests/min
└─ Fallback: DuckDuckGo (slower, free)

PostgreSQL Database
├─ Used by: All agents for state persistence
├─ Connection pool: 5-20 connections
└─ Fallback: None (SPOF - add replica?)
```

---

## 📊 Testing & Coverage

### Current Test Coverage
```
Overall:        78%  (Target: 80%+)
/agents:        85%  (Good)
/tools:         70%  (Needs improvement)
/db:            90%  (Excellent)
/guardrails:    60%  (⚠️  Critical - needs work)
```

### Missing Tests
- [ ] Output guardrails integration tests
- [ ] Summarizer tool (not built yet)
- [ ] Multi-agent coordination (not implemented)
- [ ] Error recovery scenarios

---

## 🚀 Next Steps

### Immediate (This Week)
1. Finish writer agent implementation
2. Test output guardrails thoroughly  
3. Fix researcher performance on large docs (BUGS-003)
4. Add WEB_SEARCH_API_KEY to .env

### Short Term (Next 2 Weeks)
1. Implement summarizer tool
2. Add Qdrant adapter (if needed)
3. Improve test coverage to 85%+
4. Setup basic monitoring

### Long Term (Next Month)
1. Multi-LLM debate system
2. Advanced guardrails (PII detection)
3. Monitoring dashboard
4. Load testing

---

## 🔒 Security Notes

### Implemented Guardrails
- ✅ Input validation (basic)
- ✅ Rate limiting (10 req/min)
- ✅ Prompt injection detection (basic)
- ⚠️  Output validation (needs testing)
- ❌ PII detection (not implemented)

### Security TODOs
- [ ] Test output validation guardrails
- [ ] Add PII detection for sensitive outputs
- [ ] Implement audit logging for critical actions
- [ ] Setup encryption for sensitive data

---

## 💬 Notes for Claude

### When You Read This File
- Check "Current State" first - tells you what we're working on
- Review "Recent Changes" - see what was built recently
- Check "Known Issues" - don't repeat mistakes
- Read "Don't Repeat These Mistakes" - learn from failures

### Before Making Changes
- Update "Recent Changes" when you modify code
- Add new issues to "Known Issues"
- Update file status in "Key Files & Their Status"
- Note any architectural decisions made

### Red Flags to Watch For
- ⚠️  If output_guard.py is modified, test it thoroughly
- ⚠️  If web_search.py is called frequently, check rate limits
- ⚠️  If processing document >10K words, chunk it first
- ⚠️  If cache behavior is weird, check TTL settings

---

## 📅 Update History

### [CURRENT DATE]
- Updated: Current state (working on writer agent)
- Added: Issue with output guardrails not tested
- Modified: Project structure (added writer.py)

### [PREVIOUS DATE]
- Updated: Recent changes (researcher agent completed)
- Added: Known issue with large documents
- Modified: Configuration (timeout increased to 60s)

---

**⚠️  REMEMBER TO UPDATE THIS FILE AFTER EVERY BUILD SESSION! ⚠️**

*This is Claude's memory. Keep it current or bugs will repeat.*
```

---

## 📄 File 2: .bugs_tracker.md

### Purpose
Tracks all bugs and patterns to:
- Prevent the same bug from recurring
- Identify patterns in failures
- Track resolution progress
- Document what was tried

### Template

```markdown
# Bug Tracker - [PROJECT NAME]

> Last Updated: [DATE - UPDATE WHEN BUGS FOUND/FIXED]
> Active Bugs: [COUNT]
> Resolved This Week: [COUNT]

---

## 🚨 Active Bugs (PRIORITY ORDER)

### BUGS-001: [Short Description]
**Status:** Active  
**Priority:** Critical / High / Medium / Low  
**Severity:** Blocker / Major / Minor  
**Found:** [DATE]  
**Affects:** [Component/Feature]  

**Description:**
[Clear description of the bug]

**How to Reproduce:**
1. Step 1
2. Step 2
3. Observe error

**Expected Behavior:**
[What should happen]

**Actual Behavior:**
[What actually happens]

**Error Message:**
```
[Paste full error/stack trace]
```

**Files Involved:**
- `app/agents/researcher.py` (line 45-67)
- `app/tools/web_search.py` (line 120)

**Root Cause Analysis:**
- Initial hypothesis: [What we think is wrong]
- Investigation: [What was checked]
- Confirmed cause: [What's actually wrong]

**Fix Attempts:**
1. [DATE] Tried: [What was attempted]
   - Result: [Did it work?]
   - Why it failed: [Reason]

2. [DATE] Tried: [Second attempt]
   - Result: [Did it work?]
   - Why it failed: [Reason]

**Blocked By:**
- [ ] Need to refactor X first
- [ ] Waiting for library update
- [ ] Need more test data

**Workaround (if any):**
```
# Temporary fix users can apply
if large_document:
    chunks = split_document(document, max_size=5000)
    process_chunks(chunks)
```

**Next Steps:**
- [ ] Try implementing chunking in researcher.py
- [ ] Add caching for chunks
- [ ] Write test case to verify fix

---

### BUGS-002: [Another Bug]
[Same structure as above]

---

## ✅ Resolved Bugs

### BUGS-R01: Database Connection Pool Exhaustion
**Status:** Resolved  
**Priority:** High  
**Severity:** Major  
**Found:** [DATE]  
**Fixed:** [DATE]  
**Time to Resolve:** 3 days  

**Problem:**
Application crashed after 100 requests due to connection pool exhaustion.

**Solution:**
```python
# Before (broken)
engine = create_engine(DATABASE_URL)

# After (fixed)
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

**Lessons Learned:**
- Always configure connection pooling from the start
- Monitor pool usage in production
- Set pool_recycle to prevent stale connections

**Prevention:**
- Added to project template
- Added test case for connection pool behavior
- Documented in ARCHITECTURE.md

---

### BUGS-R02: [Another Resolved Bug]
[Same structure]

---

## 🔍 Bug Patterns Identified

### Pattern 1: Large Input Handling
**Occurrences:** 3 times
**Components Affected:** researcher agent, summarizer, input validation

**Pattern:**
Functions fail when processing inputs >10K characters without chunking.

**Solution:**
Always implement chunking for text processing:
```python
MAX_CHUNK_SIZE = 5000

def process_safely(text):
    if len(text) > MAX_CHUNK_SIZE:
        chunks = chunk_text(text, MAX_CHUNK_SIZE)
        return [process(chunk) for chunk in chunks]
    return process(text)
```

**Applied To:**
- [x] researcher.py
- [ ] summarizer.py (not implemented yet)
- [x] input validation

---

### Pattern 2: Cache Invalidation Issues
**Occurrences:** 2 times
**Components Affected:** web_search tool, researcher cache

**Pattern:**
Cached data not expiring, leading to stale results.

**Solution:**
Always set explicit TTL:
```python
cache.set(key, value, ttl=3600)  # 1 hour
```

**Applied To:**
- [ ] web_search.py (needs update)
- [x] researcher cache

---

## 📊 Bug Statistics

### By Priority
- Critical: 0
- High: 1 (BUGS-003)
- Medium: 2 (BUGS-001, BUGS-002)
- Low: 1 (BUGS-004)

### By Component
- Agents: 2 bugs
- Tools: 1 bug
- Database: 0 bugs (recently fixed)
- Guardrails: 1 bug

### Resolution Time
- Average: 2.5 days
- Fastest: 2 hours (BUGS-R02)
- Slowest: 1 week (BUGS-R01)

---

## 🔧 Common Fixes Reference

### Fix 1: Reset Cache
```bash
redis-cli FLUSHALL
```
**Use when:** Stale cache data causing issues

### Fix 2: Reset Database Connections
```bash
docker-compose restart db
```
**Use when:** Connection pool exhausted

### Fix 3: Clear Test Data
```bash
pytest --cache-clear
rm -rf .pytest_cache
```
**Use when:** Tests failing due to cached results

---

## ⚠️ Known Limitations (Not Bugs)

### Limitation 1: Rate Limiting
**Component:** web_search tool  
**Limit:** 10 requests/minute  
**Impact:** Researcher agent can't search more than 10 times/min  
**Planned Fix:** Implement caching + paid tier upgrade  

### Limitation 2: Model Context Window
**Component:** researcher agent  
**Limit:** 4K tokens (GPT-4)  
**Impact:** Can't process very long documents in single call  
**Planned Fix:** Implement chunking strategy  

---

## 🎯 Prevention Checklist

Before marking a bug as "resolved":

- [ ] Fix implemented and tested
- [ ] Test case added to prevent regression
- [ ] Documentation updated (if needed)
- [ ] Code review completed
- [ ] Related components checked for same issue
- [ ] Lessons learned documented
- [ ] Prevention added to templates (if applicable)

---

## 📝 Notes for Claude

### When You See This File
- Check "Active Bugs" before modifying related code
- Review "Bug Patterns" to avoid common mistakes
- Check "Common Fixes" for quick solutions
- Add new bugs immediately when found

### Before Closing a Bug
- Verify fix with test case
- Document solution clearly
- Move to "Resolved Bugs" section
- Extract lessons learned

### Red Flags
- 🚩 If you see the same bug type 3+ times, it's a pattern
- 🚩 If a bug takes >1 week to resolve, break it down
- 🚩 If workarounds are being used long-term, prioritize fix
- 🚩 If "Active Bugs" count >10, stop adding features and fix bugs

---

## 📅 Update Log

### [CURRENT DATE]
- Added: BUGS-003 (researcher performance)
- Updated: BUGS-001 (tried new fix approach)
- Moved: BUGS-R01 to resolved (connection pool fixed)

### [PREVIOUS DATE]
- Added: BUGS-001 (cache invalidation)
- Added: BUGS-002 (output validation)
- Pattern identified: Large input handling

---

**⚠️  UPDATE THIS FILE IMMEDIATELY WHEN BUGS ARE FOUND OR FIXED! ⚠️**

*Track bugs early. Fix them faster. Prevent them from returning.*
```

---

## 🔄 Update Workflows

### Workflow 1: After Every Build Session

```bash
# 1. Update Claude Context
vim .claude-context.md

# What to update:
- Current State section (what are you working on now)
- Recent Changes section (what changed this session)
- Key Files & Their Status (mark files as working/broken)
- Known Issues (add any new issues found)

# 2. Update Bugs Tracker (if bugs found)
vim .bugs_tracker.md

# What to update:
- Add new bugs to "Active Bugs"
- Update status of existing bugs
- Move resolved bugs to "Resolved Bugs"
- Update statistics

# 3. Commit Both
git add .claude-context.md .bugs_tracker.md
git commit -m "EOD: Updated context and bugs"
```

### Workflow 2: When Bug Is Found

```bash
# 1. Add to bugs tracker
vim .bugs_tracker.md

# Include:
- Clear description
- How to reproduce
- Expected vs actual behavior
- Error messages/stack traces
- Files involved

# 2. Add to Claude context
vim .claude-context.md

# Update:
- Known Issues section (add new issue)
- Red Flags section (if critical)
- Next Steps (prioritize fixing it)

# 3. Commit
git add .bugs_tracker.md .claude-context.md
git commit -m "BUG: [Short description]"
```

### Workflow 3: When Bug Is Fixed

```bash
# 1. Update bugs tracker
vim .bugs_tracker.md

# Do:
- Move bug to "Resolved Bugs" section
- Document solution
- Extract lessons learned
- Add to prevention checklist

# 2. Update Claude context
vim .claude-context.md

# Do:
- Remove from "Known Issues"
- Add to "Lessons Learned"
- Update "Don't Repeat These Mistakes"

# 3. Commit
git add .bugs_tracker.md .claude-context.md
git commit -m "FIXED: [Bug description]"
```

---

## 📋 Quick Checklist

### Daily (Start of Work)
- [ ] Read `.claude-context.md` "Current State"
- [ ] Check `.bugs_tracker.md` "Active Bugs"
- [ ] Note any blockers or critical issues

### During Work
- [ ] When bug found → Add to `.bugs_tracker.md` immediately
- [ ] When file modified → Note in `.claude-context.md`
- [ ] When pattern noticed → Document it

### Daily (End of Work)
- [ ] Update `.claude-context.md` "Recent Changes"
- [ ] Update `.bugs_tracker.md` bug statuses
- [ ] Update `.claude-context.md` "Next Steps"
- [ ] Commit both files

### Weekly Review
- [ ] Review all active bugs (prioritize top 3)
- [ ] Check for bug patterns (3+ similar bugs = pattern)
- [ ] Update statistics
- [ ] Clean up resolved bugs older than 2 weeks

---

## 🎯 Success Metrics

### You're Doing This Right When:
✅ `.claude-context.md` updated after every build session  
✅ `.bugs_tracker.md` has <10 active bugs  
✅ Same bug never occurs twice  
✅ Bug patterns identified and prevented  
✅ Claude understands project context immediately  
✅ No need to explain architecture repeatedly  
✅ Bugs resolved 30% faster (due to tracking)  

### You're Doing This Wrong When:
❌ Files not updated for >3 days  
❌ Active bugs count >20  
❌ Same bugs recurring  
❌ Claude confused about project state  
❌ Spending time re-explaining context  
❌ Bugs taking longer to debug  

---

## 📊 Expected Impact

### Time Savings
- **30% faster debugging** - Context immediately available
- **50% fewer repeated bugs** - Patterns documented
- **20% faster onboarding** - New devs/Claude sessions start faster

### Quality Improvements
- **80% fewer context-loss bugs** - Claude remembers state
- **90% faster pattern identification** - Bugs tracked systematically
- **100% prevention of known issues** - Lessons learned applied

---

## 💡 Pro Tips

### For .claude-context.md
1. **Update "Current State" first thing each session** - Orients Claude immediately
2. **Be specific in "Files Modified"** - Include line numbers if relevant
3. **Document "Why" not just "What"** - Explain architectural decisions
4. **Keep "Red Flags" updated** - Critical issues need visibility

### For .bugs_tracker.md
1. **Add bugs immediately when found** - Don't wait
2. **Include full error messages** - Copy entire stack trace
3. **Document what was tried** - Even failed attempts are valuable
4. **Look for patterns after 3 similar bugs** - Systematic issues need systematic fixes

### For Both Files
1. **Commit often** - After every significant change
2. **Use clear commit messages** - Future you will thank you
3. **Review weekly** - Clean up old entries
4. **Cross-reference** - Link bugs in context, context in bugs

---

## 🚨 Common Mistakes to Avoid

### ❌ Don't:
- Skip updates "just this once" - Leads to stale context
- Wait until EOD to update - Forget details
- Delete old entries - History is valuable
- Use vague descriptions - "Bug in agent" → Which agent? What bug?
- Forget to commit - Changes lost = memory lost

### ✅ Do:
- Update immediately when changes made
- Be specific and detailed
- Keep history (move to archive if needed)
- Include file paths, line numbers, error messages
- Commit frequently with clear messages

---

## 🔗 Integration with Other Docs

### References in Other Files
- **00_START_HERE.md** - Links to this guide
- **01_QUICK_REFERENCE.md** - Quick checklist for updates
- **02_COMPLETE_GUIDE.md** - Full methodology
- **04_AI_ASSISTANT_INTEGRATION.md** - How AI uses these files

### Use With
- **Git workflows** - Commit context files with code
- **Code reviews** - Reference bugs tracker in PRs
- **Sprint planning** - Use "Next Steps" for planning
- **Retrospectives** - Use "Lessons Learned" for reflection

---

## 📞 Need Help?

### File Not Working As Expected?
1. Check you're updating after every session
2. Verify both files are in project root
3. Confirm AI is reading them (tell it to read them explicitly)
4. Make sure commit messages reference context/bugs

### Still Seeing Repeated Bugs?
1. Check bugs tracker for patterns
2. Verify lessons learned are applied
3. Update prevention checklist
4. Review if bugs are actually resolved

### Claude Still Confused?
1. Read .claude-context.md at start of each session
2. Explicitly reference context: "Check .claude-context.md for current state"
3. Update context immediately when confusion occurs
4. Make context more specific and detailed

---

**Remember: These files are Claude's memory. No updates = no memory = bugs repeat.**

**Make updating these files a non-negotiable habit.** 🎯

*Version 1.0.0 | Last Updated: February 2026*
