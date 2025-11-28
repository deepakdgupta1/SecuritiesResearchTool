# 🧭 Modern Engineering Standards & Best Practices

**Version:** 1.3  
**Last updated:** 2025-11-27  
**Owner:** Engineering Leadership  

**Purpose**  
This living document defines our unified standards for software engineering excellence — combining secure coding (CERT/OWASP), software quality (ISO/IEC 25010), clean code principles, and modern practices proven at scale.

**Goal**  
Deliver maintainable, reliable, observable, secure, inclusive, and cost-effective software — consistently and predictably.

## Table of Contents
- [1. Code Structure & Readability](#1-code-structure--readability)
- [2. Design & Architecture](#2-design--architecture)
- [3. Security](#3-security)
- [4. Testing & Reliability](#4-testing--reliability)
- [5. Version Control, Reviews & CI/CD](#5-version-control-reviews--cicd)
- [6. Dependencies & Environment](#6-dependencies--environment)
- [7. Documentation & Knowledge Sharing](#7-documentation--knowledge-sharing)
- [8. Non-Functional Requirements](#8-non-functional-requirements)
- [9. Inclusive & Accessible Engineering](#9-inclusive--accessible-engineering)
- [10. Incident Management & Learning](#10-incident-management--learning)
- [Enforcement & Evolution](#enforcement--evolution)

---

## 1. Code Structure & Readability

### 1.1 Naming & Style
- Use clear, intention-revealing names (`userRepository`, `calculateOrderTotal`, `retryPolicy`).
- Follow the official or de-facto style guide for each language (PEP 8, Google Java, kotlin-style, etc.).
- Avoid abbreviations unless universally recognized (`id`, `url`, `api`, `cfg`).
- One concept → one name across the codebase (never `customer` in one place and `client` in another).

### 1.2 Functions & Methods
- Each function does one thing and does it well.
- Aim for ≤ ~50 lines; extract when readability or reuse suffers (strict 20–30 line limits are counterproductive).
- Prefer parameter objects over lists longer than 4–5 parameters.
- Avoid boolean flags that change core behavior — split into separate functions instead.

### 1.3 Classes & Modules
- Single Responsibility Principle: a class/module has one reason to change.
- No god classes or `Utils` dumping grounds.
- Clear boundaries: domain ↔ application ↔ infrastructure ↔ presentation.

### 1.4 Error Handling
- Never swallow exceptions silently.
- Use structured, typed errors (domain vs. technical).
- Prefer explicit error returns or exceptions over magic values.
- Log context at the boundary, not inside libraries.

### 1.5 Comments
- Explain why, not what.
- Remove outdated comments immediately.
- Document non-obvious business rules and edge cases.

---

## 2. Design & Architecture

### 2.1 SOLID Principles
- **S**ingle Responsibility · **O**pen/Closed · **L**iskov Substitution · **I**nterface Segregation · **D**ependency Inversion

### 2.2 Clean/Hexagonal Architecture
- Dependency rule: inner layers (domain) never depend on outer layers (frameworks, DB, UI).
- Use DTOs / view models at boundaries.

### 2.3 Coupling & Cohesion
- High cohesion inside modules, low coupling between them.
- No circular dependencies.
- Prefer composition over inheritance.

### 2.4 Extensibility
- Design for known change hotspots.
- Use configuration, feature flags, and strategy/patterns instead of hard-coding.

---

## 3. Security (OWASP / CERT)

### 3.1 Input & Data
- All external input is untrusted — validate & sanitize.
- Use allow-lists for validation.
- Escape output appropriately (HTML, SQL, shell, logs).

### 3.2 Authentication & Authorization
- Never implement crypto or auth from scratch.
- Authorization enforced server-side.
- Least privilege for users and service accounts.

### 3.3 API Security
- Enforce rate limiting and abuse detection.
- Use OpenAPI spec + runtime validation.
- Strict CORS, Content-Type, and HTTP method enforcement.

### 3.4 Secrets & Credentials
- Never commit secrets to source control.
- Use managed secret stores; rotate regularly.

### 3.5 Logging & Privacy
- Structured JSON logging.
- Never log credentials, tokens, or PII.
- Mask or hash sensitive data (GDPR/CCPA compliance).

All services must satisfy at least OWASP ASVS Level 2.

---

## 4. Testing & Reliability

### 4.1 Testing Pyramid
- Heavy unit tests on domain logic.
- Integration tests for infrastructure concerns.
- Narrow end-to-end tests for critical flows.

### 4.2 Test Quality
- Deterministic, fast, isolated.
- Meaningful names, single assertion per test where practical.
- Use builders/factories for test data; avoid shared mutable state.
- Mock external systems, never hit real third-party services.

### 4.3 Coverage & Regression
- ≥ 80 % branch coverage on new/changed code.
- Every bug fix gets a regression test.
- No production merge without passing tests + review.

### 4.4 Resilience
- Timeouts on all network calls.
- Retry with exponential backoff + jitter.
- Circuit breakers or graceful degradation for non-critical dependencies.

Encourage property-based and contract testing for public APIs and critical domain models.

---

## 5. Version Control, Reviews & CI/CD

### 5.1 Git Hygiene
- Small, focused commits with imperative messages.
- Branch naming: `feature/`, `bugfix/`, `hotfix/`, `chore/`.
- Trunk-based development preferred; feature branches < 2 days.
- Incomplete features behind feature flags.

### 5.2 Code Reviews
- Mandatory peer review for all production code.
- Focus: correctness, security, testing, readability.
- Linters handle pure style.

### 5.3 CI/CD
Every push must pass:
- Formatting & linting
- Unit + integration tests
- Static analysis (CodeQL, SonarQube, dependency scanning)
- SBOM generation

Automated promotion with blue/green or canary where possible; rollback plan mandatory.

---

## 6. Dependencies & Environment

### 6.1 Dependency Management
- Pin versions (lockfiles).
- Automated security scanning; fail on critical vulnerabilities.
- Quarterly cleanup of unused dependencies.
- SBOM generated and stored for every build.

### 6.2 Licensing
- Track and approve all third-party licenses.
- No GPL or other viral licenses without legal sign-off.

### 6.3 Environment Parity
- Dev ≈ Staging ≈ Prod.
- Infrastructure as Code + containers.
- All configuration via environment variables or config service.

---

## 7. Documentation & Knowledge Sharing

### 7.1 Code Documentation
- Clear docstrings/comments for public APIs.
- Explain algorithms and business rules.
- Explain the purpose of each class and method.

### 7.2 Architecture Documentation
- C4 model diagrams kept current.
- Architecture Decision Records (ADRs) for every significant choice.

### 7.3 Onboarding & Operations
- “How to run locally” in README.
- Runbooks for common operations and incidents.

---

## 8. Non-Functional Requirements

### 8.1 Performance & Scalability
- Define SLIs/SLOs for latency, throughput, error budgets.
- Load test critical paths before major releases.

### 8.2 Observability
- Centralized logs, metrics, traces.
- Meaningful dashboards + alerting on error rates, latency, saturation.

### 8.3 Technical Debt
- Tracked and prioritized like features.
- Refactoring is normal work, not “extra”.

### 8.4 Cost & Sustainability
- Include cost and carbon impact in ADRs for infrastructure changes.
- Right-size resources; clean up orphans.

---

## 9. Inclusive & Accessible Engineering

- Use inclusive language in code, comments, docs, and UIs.
- Customer-facing UI must meet WCAG 2.1 AA.
- Logs and CLIs avoid color-only indicators.

---

## 10. Incident Management & Learning

- Blameless postmortems for all P0/P1 incidents.
- Every postmortem produces ≥ 1 actionable, tracked follow-up.
- Share learnings widely.

---

## 11. Python Specific Standards

### 11.1 Project Layout & Dependencies
- **Structure:** The `src` layout is mandatory (`src/my_project/`).
- **Dependency Management:**
  - Allowed tools: **uv**, **pip-tools**, or **poetry**.
  - **Lockfiles:** Must be committed and include hashes.
  - **Forbidden:** No bare `requirements.txt` allowed in production repositories.
  - **Packaging:** Build wheels only (no sdists in production).

### 11.2 Style, Formatting & Linting
- **Line Length:** 100 characters.
- **Formatter:** **Black** (`black --check`).
- **Linter:** **Ruff** (version ≥ 0.6).
  - Must select `"ALL"` rules with minimal ignores.
  - Command: `ruff check`.

### 11.3 Type Safety
- **Strict Compliance:** 100% type coverage required for all new or changed code.
- **Tools:** **Mypy** in strict mode is mandatory. **Pyright** is optional but encouraged.
- **Prohibitions:** No `Any`, `# type: ignore`, or unnecessary `cast(...)` usage without a linked ticket and comment.

### 11.4 Testing & Reliability
- **Framework:** **pytest** + **pytest-cov**.
- **Coverage:** Target ≥ 95% branch coverage on new code.
- **Methodology:**
  - Property-based testing (**Hypothesis**) encouraged for domain logic.
  - Snapshot testing (**Syrupy**) is allowed.

### 11.5 Async & Concurrency
- **Frameworks:** Prefer **anyio** or **trio** for new async services.
- **Safety:** Never mix blocking I/O in async code without explicitly offloading it.
- **HTTP Client:** Use **httpx** (Async-first).

### 11.6 Security & Forbidden Patterns
| Pattern | Reason | Allowed Alternative |
| :--- | :--- | :--- |
| `print()` | Pollutes logs | **structlog** |
| `eval()` / `exec()` | Security risk | None |
| `pickle` | Insecure/Brittle | **msgpack**, **orjson**, **Protobuf** |
| `subprocess` (unsafe) | Injection risk | `subprocess.run(..., check=True, shell=False)` |

### 11.7 Recommended Stack (2025 Standard)
- **HTTP API:** **FastAPI** (with Pydantic v2).
- **Task Queue:** **arq** (default), dramatiq, or Celery.
- **Settings:** **Pydantic v2 Settings** (Single source of truth).
- **ORM:** **SQLModel** or **Tortoise-ORM** (Type-safe, lightweight).
- **Logging:** **structlog** (Must output JSON in production).

### 11.8 Deployment Containers
- **Base Image:** `python:3.11-slim-bookworm` (or official slim variant).
- **Structure:** Multi-stage Dockerfiles are mandatory.

---

## Enforcement & Evolution

- Maximum automation: linters, formatters, pre-commit hooks, CI gates.
- This document is reviewed quarterly (or after major incidents).
- Exceptions require an ADR and leadership approval.
- Engineers are empowered (and expected) to propose improvements.

> “Clean code always looks like it was written by someone who cares.”  
> — Michael Feathers

---