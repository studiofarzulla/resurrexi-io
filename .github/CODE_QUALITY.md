# Code Quality & Testing Guide

## Overview

Papers with computational components maintain high code quality standards through automated testing, linting, and continuous integration.

## Projects with Full CI/CD

### 🏆 ASRI (Tier 1 - Production)
**Path:** `asri/code/`  
**Tech:** Python 3.11+, FastAPI, PostgreSQL, React frontend

**CI Features:**
- ✅ Unit tests with 70%+ coverage requirement
- ✅ Integration tests with PostgreSQL
- ✅ Type checking (mypy in strict mode)
- ✅ Linting (ruff)
- ✅ Security scanning (Bandit, Safety)
- ✅ Code complexity checks (radon, xenon)
- ✅ Frontend build & tests

**Run Locally:**
```bash
cd asri/code
pip install -e ".[dev,all]"
pytest tests/ -v --cov
ruff check .
mypy src/
```

### 📊 Event Study (Tier 1 - Analysis)
**Path:** `event-study/code/`  
**Tech:** Python 3.10+, pandas, statsmodels, GARCH models

**CI Features:**
- ✅ Analysis script smoke tests
- ✅ Data integrity validation
- ✅ Reproducibility checks
- ✅ Linting (flake8, black)

**Run Locally:**
```bash
cd event-study/code
pip install -r requirements.txt
pytest tests/ -v
black --check .
python data_preparation.py  # Verify scripts run
```

### 🤖 Extremity ABM (Tier 1 - Simulation)
**Path:** `extremity-abm/code/`  
**Tech:** Python 3.10+, Mesa, Kafka, sentiment analysis

**CI Features:**
- ✅ Unit tests with 80%+ coverage requirement
- ✅ Performance benchmarks
- ✅ Memory usage tests
- ✅ Simulation smoke tests
- ✅ Timeout protection (300s)

**Run Locally:**
```bash
cd extremity-abm/code
pip install -r requirements.txt
pytest tests/ -v --cov
pytest tests/ -v -m performance  # Benchmarks
```

### 📄 Whitepaper Claims (Tier 2 - Analysis)
**Path:** `whitepaper-claims/code/`  
**Tech:** Python, NLP, factor analysis

**CI Features:**
- ✅ Basic testing (60%+ coverage)
- ✅ NLP model tests
- ✅ Data-intensive test markers

**Run Locally:**
```bash
cd whitepaper-claims/code
pip install -r requirements.txt
pytest tests/ -v -m "not data_intensive"  # Skip large data tests
```

## Pre-commit Hooks

Install once at repository root:
```bash
cd ~/Resurrexi/projects/papers/papers-official
pip install pre-commit
pre-commit install
```

**Hooks automatically run on commit:**
- Python formatting (ruff)
- Type checking (mypy for ASRI)
- LaTeX indentation
- BibTeX validation
- Large file detection (50MB limit)
- Secret detection
- Frozen submission protection ⚠️

**Run manually on all files:**
```bash
pre-commit run --all-files
```

**Skip hooks (use sparingly):**
```bash
git commit --no-verify -m "Emergency fix"
```

## Code Quality Standards

### Python

**Style:**
- Ruff for linting & formatting (replaces black, flake8, isort)
- Line length: 100 chars (ASRI), 127 chars (others)
- Type hints required for ASRI, encouraged for others

**Testing:**
- Use pytest with markers: `@pytest.mark.slow`, `@pytest.mark.integration`
- Aim for 60%+ coverage (70%+ for ASRI)
- Fast tests (<1s) by default, mark slow tests
- Use fixtures for common setup

**Complexity:**
- Cyclomatic complexity: ≤15 per function
- Maintainability index: ≥65
- ASRI enforces: max-absolute B, max-modules A

**Example Test:**
```python
import pytest

def test_calculation():
    """Fast unit test."""
    result = calculate_metric(data=[1, 2, 3])
    assert result == 2.0

@pytest.mark.slow
@pytest.mark.integration
def test_full_pipeline():
    """Integration test requiring data."""
    pipeline = AnalysisPipeline()
    results = pipeline.run()
    assert len(results) > 0
```

### LaTeX

**Standards:**
- Auto-indent with latexindent (pre-commit)
- BibTeX entries validated
- 4-pass compilation for citations
- No modification of frozen submissions

### JavaScript (ASRI Frontend)

**Standards:**
- ESLint for linting
- npm audit for security
- Build must succeed
- Tests (when configured)

## CI/CD Workflows

### On Every Push/PR

**All Papers:**
- LaTeX build check
- Python general testing
- Paper status validation

**ASRI:**
- Full test suite (unit + integration)
- Frontend build
- Security scans
- Code quality metrics

**Event Study:**
- Analysis validation
- Reproducibility checks
- Data integrity

**Extremity ABM:**
- Test suite
- Performance benchmarks

### Monthly

**All Projects:**
- Dependency updates via Dependabot
- Security vulnerability scans

## Adding Tests to a New Paper

### 1. Create Test Structure
```bash
cd your-paper/code
mkdir tests
touch tests/__init__.py
touch tests/test_basic.py
```

### 2. Add pytest.ini
Copy from `event-study/code/pytest.ini` or `whitepaper-claims/code/pytest.ini`

### 3. Write First Test
```python
# tests/test_basic.py
import pytest

def test_imports():
    """Verify main modules import."""
    import your_module
    assert your_module is not None

def test_basic_calculation():
    """Test core functionality."""
    from your_module import calculate
    result = calculate([1, 2, 3])
    assert result > 0
```

### 4. Add to CI
Edit `.github/workflows/python-tests.yml`:
```yaml
matrix:
  project:
    - asri/code
    - your-paper/code  # Add here
```

### 5. Configure Pre-commit
Pre-commit will automatically format Python in `your-paper/code/`

## Debugging CI Failures

### "ModuleNotFoundError"
- Check `requirements.txt` or `pyproject.toml` includes all dependencies
- Verify Python version compatibility

### "Coverage Failed"
- Lower `--cov-fail-under` in `pytest.ini` temporarily
- Add more tests to increase coverage

### "Type Check Failed"
- Add `# type: ignore` comments for complex types
- Or exclude file from mypy in `pyproject.toml`

### "LaTeX Build Failed"
- Check for missing packages
- Review build logs in Actions → Artifacts

### "Pre-commit Failed Locally"
- Run `pre-commit run --all-files` to see details
- Update hooks: `pre-commit autoupdate`
- Skip protected files: already configured in `.pre-commit-config.yaml`

## Code Quality Badges

Add to README files:

```markdown
[![Tests](https://github.com/studiofarzulla/resurrexi-io/actions/workflows/asri-full-ci.yml/badge.svg)](https://github.com/studiofarzulla/resurrexi-io/actions/workflows/asri-full-ci.yml)
[![codecov](https://codecov.io/gh/studiofarzulla/resurrexi-io/branch/master/graph/badge.svg)](https://codecov.io/gh/studiofarzulla/resurrexi-io)
```

## Performance Optimization

### Slow Tests
```bash
# Find slowest tests
pytest --durations=10

# Skip slow tests during development
pytest -m "not slow"
```

### Parallel Testing
```bash
pip install pytest-xdist
pytest -n auto  # Use all CPU cores
```

### Profile Code
```bash
pip install pytest-profiling
pytest --profile
```

## Security Best Practices

1. **Never commit secrets** - pre-commit checks for this
2. **Pin dependencies** - use `pip freeze` or `poetry.lock`
3. **Review Bandit warnings** - especially for data handling code
4. **Run Safety checks** - `safety check` in your virtualenv
5. **Audit npm packages** - `npm audit` in frontend directories

## Resources

- **pytest docs:** https://docs.pytest.org/
- **ruff docs:** https://docs.astral.sh/ruff/
- **pre-commit:** https://pre-commit.com/
- **mypy:** https://mypy.readthedocs.io/
- **Coverage.py:** https://coverage.readthedocs.io/
