# Version Control & Collaboration
### Git Workflow

**Branching Strategy:**
- `main` branch: Production-ready code
- `develop` branch: Integration branch for features
- Feature branches: `feature/pattern-vcp-detector`
- Bugfix branches: `bugfix/indicator-calculation-error`
- Hotfix branches: `hotfix/security-patch-001`

**Branch Naming:**
- Use descriptive names
- Include ticket/issue number if applicable: `feature/PROJ-123-add-double-bottom-pattern`

### Commit Messages

**Format: Conventional Commits**
```
<type>(<scope>): <short description>

<optional longer description>

<optional footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `docs`: Documentation changes
- `chore`: Build/tooling changes

**Examples:**
```
feat(patterns): add VCP detector with configurable tolerance

fix(indicators): correct Mansfield RS calculation for edge case

refactor(backtesting): extract position management into separate class
```

### Code Review Process

**Mandatory for all production code:**
- All pull requests require at least 1 approval
- Review checklist:
  - [ ] Code follows style guide (black, flake8 pass)
  - [ ] Tests added/updated (coverage ≥80%)
  - [ ] Documentation updated
  - [ ] No security vulnerabilities introduced
  - [ ] Performance acceptable

**Focus Areas:**
- Correctness of logic
- Security implications
- Test coverage and quality
- Readability and maintainability
- (Linters handle pure style)

### Trunk-Based Development (Future)

**For MVP:** Feature branches merged to main

**Post-MVP:** Short-lived feature branches (<2 days), frequent integration, feature flags for incomplete features

---
