# GitHub Infrastructure Setup Summary

## What Was Created

### 1. GitHub Copilot Instructions
**File:** `.github/copilot-instructions.md`

Comprehensive guide for AI assistants covering:
- Repository structure (5 research programmes)
- Build/test commands for LaTeX, Python, JavaScript, R
- Key conventions (canonical files, frozen submissions, archive structure)
- Paper numbering system and external references
- Development workflow and testing strategy

### 2. GitHub Actions Workflows

#### LaTeX Build Check (`.github/workflows/latex-build.yml`)
- Builds PDFs for major papers on push/PR
- Validates BibTeX syntax
- Uploads PDF artifacts (7-day retention)
- Matrix build for multiple papers

#### Python Code Quality (`.github/workflows/python-tests.yml`)
- Tests Python 3.11 & 3.12
- Runs pytest with coverage
- Linting with ruff
- Type checking with mypy
- Security scanning with Bandit & TruffleHog
- Codecov integration

#### Paper Status Tracking (`.github/workflows/paper-tracking.yml`)
- Validates CLAUDE.md structure
- Checks canonical files exist
- Verifies submission directory protection
- Generates paper statistics (arXiv, Under Review, etc.)
- Tracks Lean formalizations

### 3. Issue Templates

- **Paper Revision** (`.github/ISSUE_TEMPLATE/paper-revision.md`) — Track LaTeX edits, citations, figures
- **Code Bug** (`.github/ISSUE_TEMPLATE/code-bug.md`) — Report bugs in analysis code
- **New Paper** (`.github/ISSUE_TEMPLATE/new-paper.md`) — Track new research paper development

### 4. Pull Request Template
**File:** `.github/PULL_REQUEST_TEMPLATE.md`

Checklist-driven PR template ensuring:
- Canonical file edits (not archived versions)
- Submission directory protection
- Testing requirements
- Proper paper ID references

### 5. Dependabot Configuration
**File:** `.github/dependabot.yml`

Automated dependency updates for:
- Python (pip) — asri, event-study, whitepaper-claims, no-structure
- JavaScript (npm) — asri frontend
- GitHub Actions — workflow dependencies

Monthly update schedule, limited to 5 PRs per ecosystem.

### 6. Code Owners
**File:** `.github/CODEOWNERS`

- Default owner: @studiofarzulla
- ASRI co-ownership: @andrew-maksakov
- Protected submission directories
- Master index requires review

## Next Steps

### 1. Push to GitHub
```bash
cd ~/Resurrexi/projects/papers/papers-official
git push origin master
```

### 2. Enable GitHub Actions
- Visit repository settings → Actions → Enable workflows
- First workflow runs will validate current state

### 3. Configure Secrets (Optional)
If using Codecov or other integrations:
- Settings → Secrets and variables → Actions
- Add `CODECOV_TOKEN` if you want coverage reports

### 4. Create Initial Issues
Use the new issue templates to:
- Track ongoing paper revisions
- Log any known code bugs
- Plan new papers in development

### 5. Set Up Branch Protection (Optional)
For collaborative work:
- Settings → Branches → Add rule
- Require PR reviews before merging
- Require status checks (CI workflows)

### 6. Configure GitHub Pages (Optional)
If you want to publish paper PDFs or documentation:
- Settings → Pages
- Source: GitHub Actions
- Add a deployment workflow

## Workflow Examples

### When Editing a Paper
1. Create issue: "Paper Revision" template
2. Make changes to canonical file (check CLAUDE.md)
3. Create PR referencing issue
4. CI builds PDF and runs tests
5. Review PDF artifact from workflow
6. Merge after approval

### When Adding New Analysis Code
1. Create issue: "Code Bug" or "New Paper" template
2. Add code with tests in `<paper>/code/`
3. Create PR
4. CI runs pytest, ruff, mypy, security scans
5. Review coverage report
6. Merge after tests pass

### When Publishing to arXiv
1. Update CLAUDE.md with arXiv ID
2. Create frozen submission directory
3. PR triggers paper tracking workflow
4. Statistics updated automatically

## Customization

### Add More Papers to LaTeX Workflow
Edit `.github/workflows/latex-build.yml`:
```yaml
matrix:
  paper:
    - asri/paper
    - your-new-paper/paper  # Add here
```

### Add More Python Projects to Testing
Edit `.github/workflows/python-tests.yml`:
```yaml
matrix:
  project:
    - asri/code
    - your-new-paper/code  # Add here
```

### Adjust Dependabot Frequency
Edit `.github/dependabot.yml` — change `interval: "monthly"` to `"weekly"` or `"daily"` if desired.

## Troubleshooting

### LaTeX Build Fails
- Check if paper uses non-standard packages
- Verify file paths in workflow YAML
- Review artifact logs in Actions tab

### Python Tests Fail
- Ensure `requirements.txt` or `pyproject.toml` exists
- Check Python version compatibility (3.11/3.12)
- Verify test discovery (`tests/` directory)

### Paper Tracking Shows Warnings
- Normal if papers are in progress
- Verify canonical files match CLAUDE.md entries
- Update CLAUDE.md if file locations changed

## References

- GitHub Actions Docs: https://docs.github.com/en/actions
- Dependabot Docs: https://docs.github.com/en/code-security/dependabot
- Issue Templates: https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests
- Copilot Instructions: https://docs.github.com/en/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot
