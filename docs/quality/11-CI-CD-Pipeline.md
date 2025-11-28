# CI/CD Pipeline
Automated testing, linting, and security scanning on every commit.

### Pre-Commit Hooks

**Install pre-commit framework:**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=100]
        
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: detect-private-key  # Prevent committing secrets
```

### CI Pipeline Stages

1. **Lint & Format Check** - Code style validation
2. **Type Checking** - Static type analysis with mypy
3. **Unit Tests** - Fast isolated tests
4. **Integration Tests** - Component interaction tests
5. **Coverage Check** - Enforce ≥80% coverage
6. **Security Scanning** - SAST (Static Application Security Testing)
7. **Dependency Scanning** - Vulnerable dependencies check

### Deployment Strategy (Future)

**For MVP:** Manual deployment to localhost

**Post-MVP:**
- Blue/green deployment for zero-downtime
- Automated rollback on error rate spike
- Database migrations via Alembic

---
