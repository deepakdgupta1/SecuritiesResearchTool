# Documentation Requirements
### Code Documentation
- **Docstrings:** All public classes and methods (Google style)
- **Type Hints:** Throughout codebase (enforced by mypy)
- **Inline Comments:** Explain "what" and "why" - especially for complex algorithms
- **Complexity Analysis:** For performance-critical algorithms

### Architecture Documentation

**C4 Model Diagrams:**
- Context diagram (system in environment)
- Container diagram (web app, database, external APIs) - Already included in this TDD
- Component diagram (major modules within backend)
- Keep diagrams up-to-date with changes

**Architecture Decision Records (ADRs):**  
Document significant architectural decisions using ADR format:

```markdown
# ADR-001: Use PostgreSQL with TimescaleDB for Time-Series Data

## Status
Accepted

## Context
Need to store 5M+ rows of OHLCV data with efficient querying.

## Decision
Use PostgreSQL with TimescaleDB extension.

## Consequences
+ Optimized for time-series queries
+ Mature ecosystem
+ Scales to millions of rows
- Requires PostgreSQL (can't use MySQL/SQLite)
- Learning curve for TimescaleDB-specific features
```

````markdown
## ADR-002: Centralized Constants in constants.py

### Status
**Accepted** (2025-11-27)

### Context

During initial development, the application accumulated numerous tunable parameters scattered throughout the codebase as inline "magic numbers":

**Problems Identified:**
- Pattern detection thresholds (`if rs > 70`, `if price > low * 1.30`) embedded in logic
- Risk management settings (`stop_loss = 0.10`, `max_positions = 10`) hardcoded
- Performance targets, API timeouts, retry configurations duplicated across modules
- No documentation explaining parameter meanings or rationale

**Impact:**
- **Parameter Tuning:** Required searching entire codebase to find/change values
- **Understanding:** New developers couldn't tell why specific values were chosen
- **Testing:** Difficult to test edge cases without modifying production code
- **Strategy Variations:** Creating different trading strategies required code changes, not config changes
- **Maintenance:** Risk of inconsistent values (e.g., stop-loss in one place = 0.10, another = 0.08)

**Example of Problem Code:**
```python
def check_trend_template(metrics):
    # Magic numbers - what do they mean? Why these values?
    return (
        metrics['rs'] > 70 and
        metrics['price'] > metrics['low_52w'] * 1.30 and
        metrics['price'] > metrics['high_52w'] * 0.75
    )
```

### Decision

Create `backend/core/constants.py` module containing all application constants:

**Organization:**
- Group constants by functional category (Pattern Recognition, Risk, Performance, etc.)
- Use UPPER_SNAKE_CASE naming convention
- Provide comprehensive docstring for each constant explaining:
  - What it controls
  - Why this value was chosen
  - Safe range for modification

**Example:**
```python
# Pattern Recognition - Minervini Trend Template
TREND_TEMPLATE_RS_THRESHOLD = 70
"""
Minimum Mansfield RS rating for Trend Template qualification.

Rationale:
    - Mark Minervini uses RS > 70 as baseline for Stage 2 leaders
    - Value of 70 means stock outperformed 70% of market
    - Higher values (80-90) = stricter filter, fewer but stronger candidates

Range: 60-90 (below 60 = too many weak stocks, above 90 = too few candidates)
"""
```

**Import and Use:**
```python
from backend.core.constants import (
    TREND_TEMPLATE_RS_THRESHOLD,
    TREND_TEMPLATE_PRICE_ABOVE_52W_LOW_PCT
)

def check_trend_template(metrics):
    """Check Minervini Trend Template criteria."""
    return (
        metrics['rs'] > TREND_TEMPLATE_RS_THRESHOLD and  # Clear intent
        metrics['price'] > metrics['low_52w'] * TREND_TEMPLATE_PRICE_ABOVE_52W_LOW_PCT
    )
```

### Consequences

#### Positive

✅ **Single Source of Truth**
- All tunable parameters in one file
- Change once, affects entire application
- No risk of inconsistent values

✅ **Self-Documenting Code**
- Constant names convey meaning (`TREND_TEMPLATE_RS_THRESHOLD` vs `70`)
- Docstrings explain rationale
- New developers understand intent immediately

✅ **Easy Strategy Variations**
- Modify constants only, no code changes
- Test different parameters quickly
- Create strategy profiles (aggressive vs conservative)

✅ **Better Testing**
- Mock constants for edge case testing
- Test behavior at boundary values
- No need to modify production code for tests

✅ **Clear Separation of Concerns**
- `constants.py` = tunable parameters (what values to use)
- Business logic = how to use those values
- Configuration = environment-specific settings (API keys, DB URLs)

#### Negative

⚠️ **Additional Imports**
- Every module using constants needs import statement
- Slightly more verbose than inline values
- *Mitigation:* IDE auto-import, minimal overhead

⚠️ **Initial Extraction Effort**
- Required identifying ~60 constants across codebase
- Writing comprehensive docstrings for each
- *Mitigation:* One-time effort, long-term benefit

#### Neutral

📌 **Not a Configuration File**
- Constants are code (committed to repo), not user config
- Environment variables still used for deployment-specific values (API keys)
- Users don't modify constants - developers do

### Alternatives Considered

####Alternative 1: Configuration File (YAML/JSON)

```yaml
# config.yaml
pattern_recognition:
  trend_template_rs_threshold: 70
  vcp_min_contractions: 2
```

**Rejected Because:**
- ❌ Needs parsing/validation code
- ❌ No type safety
- ❌ Harder to document rationale inline
- ❌ Constants are code, not user configuration

**When to Use:** User-facing settings (report format, chart preferences)

#### Alternative 2: Environment Variables

```python
TREND_TEMPLATE_RS_THRESHOLD = int(os.getenv('RS_THRESHOLD', '70'))
```

**Rejected Because:**
- ❌ 60+ environment variables too unwieldy
- ❌ No centralized documentation
- ❌ Type conversion  required, error-prone
- ❌ Hard to version control (env vars not in repo)

**When to Use:** Deployment-specific values (API keys, database URLs, environment names)

#### Alternative 3: Class Constants

```python
class PatternConfig:
    RS_THRESHOLD = 70
    VCP_MIN_CONTRACTIONS = 2
```

**Rejected Because:**
- ❌ Constants scattered across multiple classes
- ❌ No single place to view all parameters
- ❌ Harder to search/modify

**When to Use:** Constants tightly coupled to specific class behavior

#### Alternative 4: Keep Inline (Status Quo)

**Rejected Because:**
- ❌ All the problems listed in Context section
- ❌ Doesn't scale as application grows
- ❌ Poor developer experience

---

### Implementation Notes

**File Structure:**
```python
# backend/core/constants.py

# ============================================================================
# PATTERN RECOGNITION THRESHOLDS
# ============================================================================

TREND_TEMPLATE_RS_THRESHOLD = 70
"""Minimum RS for Trend Template (Minervini baseline)."""

# ============================================================================
# RISK MANAGEMENT
# ============================================================================

INITIAL_STOP_LOSS_PCT = 0.10
"""Initial stop-loss as % below entry (10% = aggressive but common)."""

# ... (60+ more constants with documentation)
```

**Import Convention:**
```python
# Explicit imports (preferred)
from backend.core.constants import (
    TREND_TEMPLATE_RS_THRESHOLD,
    INITIAL_STOP_LOSS_PCT
)

# Avoid wildcard import
from backend.core.constants import *  # ❌ Don't do this
```

---

### Monitoring & Evolution

**Track Usage:**
- Log when constants are referenced (in debug mode)
- Identify which constants are never used (candidates for removal)

**Future Enhancements:**
- **Phase 2:** Add environment variable overrides for specific constants
- **Phase 3:** Create strategy profiles (conservative.py, aggressive.py)
- **Phase 4:** UI for strategy parameter tuning (still writes to constants file)

**Review Cadence:**
- Review constant values quarterly
- Update based on backtest performance
- Docstring accuracy review (ensure rationale still valid)

---

### References

- **File:** `backend/core/constants.py`
- **Related ADRs:** None yet
- **Discussions:** Team meeting 2025-11-20 (unanimous approval)
- **External Resources:**
  - Mark Minervini "Trend Template" criteria
  - Van Tharp position sizing research
````

### User Documentation

**README.md:**
- Project overview
- **How to run locally** (step-by-step setup instructions)
- Technology stack
- Project structure
- Quick start guide

**User Manual:**
- Guide to using the web UI
- Understanding ideas.csv output
- Interpreting backtest results
- Configuration options

**Troubleshooting Guide:**
- Common errors and solutions
- Database connection issues
- API rate limit handling
- Performance tuning tips

### Operational Documentation

**Runbooks:**  
Standard operating procedures for:
- Daily data update process
- Database backup and restore
- Handling pattern detection failures
- Performance degradation response

**Example Runbook Entry:**
```markdown
## Runbook: Daily Data Update Failure

### Symptoms
- No new data in database for current date
- Error logs showing API timeout

### Diagnosis
1. Check logs/application.log for errors
2. Verify Zerodha/Yahoo Finance API status
3. Check internet connectivity

### Resolution
1. If API rate limit: Wait and retry
2. If network issue: Fix network, re-run ingestion script
3. If data provider outage: Wait for service restoration
4. Manual re-run: `python scripts/data_ingestion.py --date YYYY-MM-DD`
```

### Technical Documentation

- **This TDD:** Architecture overview
- **Database Schema Documentation:** Entity-relationship diagrams, table constraints
- **API Documentation:** Auto-generated via FastAPI (OpenAPI/Swagger)
- **Algorithm Explanations:** Detailed docs for VCP detection, Trend Template logic, etc.

---
