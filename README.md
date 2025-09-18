# 🤖 Automated Pull Request Reviewer (Multi-language)

A real-world, recruiter-friendly project: a **GitHub Actions bot** that automatically reviews Pull Requests and posts a **single, human-readable comment** with code quality results. It checks **Python, JavaScript/TypeScript, and C/C++** files and can block merging if issues are found.

## What it does
- Detects changed files in the PR (diff vs base branch)
- **Python**: `flake8`, `black --check`, `pytest` (if `tests/` exists)
- **JS/TS**: `eslint`, `prettier --check` (if `package.json` exists)
- **C/C++**: `cpplint`, `clang-format --dry-run --Werror`
- Posts a **single summary comment** on the PR with all results
- Fails the job if there are issues → optional merge gate

## Quick start
1. Copy into your repo:
   - `.github/workflows/quality-bot.yml`
   - `scripts/pr_review_bot.py`
   - `requirements.txt`
2. Commit & push. On each PR, the bot installs tools, analyzes changed files, and comments with results.
3. No extra secrets required; it uses GitHub's `GITHUB_TOKEN`.

## Why this is “real impact”
- Saves reviewer time by surfacing formatting/lint/test issues automatically.
- Works across languages and repos; keeps feedback in **one comment**.
- Easy to extend with SCA (`pip-audit`, `npm audit`), coverage, or org rules.

## CV blurb
**Automated Pull Request Reviewer (GitHub Actions)** — Built a CI bot that analyzes changed files in PRs (Python, JS/TS, C/C++) using flake8, black, pytest, ESLint, Prettier, cpplint, and clang-format, and posts a single summary comment via the GitHub API. Reduced manual review time and improved code quality with an optional merge gate.

License: MIT
