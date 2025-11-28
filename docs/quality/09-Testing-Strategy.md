# Testing Strategy
Following the testing pyramid approach: heavy unit tests, moderate integration tests, minimal E2E tests.

### Testing Levels

#### Unit Tests
**Scope:** Individual functions and classes in isolation

**Coverage Target:** ≥80% branch coverage for new/changed code

**Characteristics:**
- Fast (entire suite runs in < 10 seconds)
- Deterministic (no flakiness)
- Isolated (no external dependencies, mock all I/O)

**What to Test:**
- Pattern recognition logic (each pattern detector)
- Indicator calculations (MA, RSI, MACD, Mansfield RS)
- Risk management rules (stop-loss calculations)
- Performance metrics calculations
- Data validation logic

#### Integration Tests
**Scope:** Multiple components working together

**What to Test:**
- Data ingestion → database storage → retrieval
- Indicator calculation pipeline (raw data → derived metrics)
- Pattern scanner → database → ideas.csv output
- Backtesting engine full flow

#### End-to-End Tests
**Scope:** Full user workflows via API/UI

**What to Test:**
- Complete backtest workflow (API call → results → CSV download)
- Daily batch processing job
- Ideas generation and retrieval

### Test Quality Principles

**From Engineering Standards:**
- Tests must be deterministic (no random failures)
- Use builders/factories for test data
- Avoid shared mutable state between tests
- Mock external systems (never hit real APIs in tests)
- Meaningful test names that describe behavior

### Continuous Testing

- All tests run on every commit (CI/CD)
- Pre-commit hooks run fast unit tests
- Code coverage tracked and reported
- Regression tests for every bug fix
- Property-based testing for critical algorithms (future)

---
