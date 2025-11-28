# Code Quality Standards
This project follows SOLID principles and clean architecture patterns as defined in our [Engineering Standards][def].

### SOLID Principles Application

**Single Responsibility Principle (SRP):**
- Each class has one reason to change
- Pattern recognizers focus only on pattern detection
- Data providers only fetch data
- Risk managers only handle risk logic

**Open/Closed Principle (OCP):**
- Pattern recognizers extend abstract base class
- New patterns added without modifying existing code
- Strategy pattern for entry/exit rules

**Liskov Substitution Principle (LSP):**
- All DataProvider implementations are interchangeable
- YahooFinanceProvider and ZerodhaProvider can substitute each other

**Interface Segregation Principle (ISP):**
- Focused interfaces (PatternRecognizer, DataProvider, RiskManager)
- Clients depend only on methods they use

**Dependency Inversion Principle (DIP):**
- High-level modules depend on abstractions (ABC classes)
- Database access through repository pattern
- Dependency injection for testability

### Clean Architecture Layers

```
┌─────────────────────────────────────────┐
│  Presentation Layer (FastAPI, Web UI)  │
├─────────────────────────────────────────┤
│  Business Logic Layer                   │
│  - Pattern Recognition                  │
│  - Backtesting Engine                   │
│  - Risk Management                      │
├─────────────────────────────────────────┤
│  Data Layer (Database, API Clients)    │
└─────────────────────────────────────────┘
```

**Dependency Rule:** Inner layers never depend on outer layers

### Code Style & Documentation

**Python Style:**
- Follow PEP 8 strictly
- Use `black` formatter (line length: 100)
- Use `flake8` for linting
- Use `mypy` for type checking

**Documentation Requirements:**
- Docstrings for all public classes and methods (Google style)
- Type hints throughout codebase
- Inline comments explain both - "what" and "why"
- Complex algorithms include complexity analysis

---
