# AGENTS.md
Guidance for coding agents working in `local_dashboard`.

## Project Snapshot
- Language: Python (stdlib-only backend), plus inline HTML/CSS/JS in `template.py`.
- Runtime: one HTTP server process with background sampler threads.
- Deployment: copy package to `/usr/local/lib/local_dashboard`, run via systemd.
- Production entrypoint: `python3 -m local_dashboard`.
- Data sources: `/sys/class/power_supply/*` and `/proc/*`.
- Design intent: minimal, offline-first battery + process telemetry dashboard.

## Repository Layout
- `__main__.py`: package entrypoint that calls `server.main()`.
- `server.py`: HTTP routes, static serving, JSON APIs, thread startup.
- `battery.py`: battery reads, conservation mode helpers, ETA calculation, sampler loop.
- `procs.py`: process CPU sampling and estimated power attribution.
- `config.py`: all environment-driven constants and file paths.
- `template.py`: full frontend template and JS behavior in one string.
- `Makefile`: install/deploy/service lifecycle.
- `local-dashboard.service`: systemd unit defaults.
- `static/`: local Tailwind runtime and IBM Plex fonts for offline UI.

## Build / Run / Lint / Test Commands
There is no separate build pipeline; lifecycle is Makefile-driven.

### Install and service commands
- Full install (download assets, copy package, install service, restart): `make` or `make install`
- Asset download only: `make download`
- Copy package only: `make copy`
- Install systemd service only: `make service`
- Restart service: `make restart`
- Service status: `make status`
- Follow logs: `make logs`
- Uninstall service + files: `make uninstall`

### Local dev run (without systemd)
- From parent directory of this repo: `python3 -m local_dashboard`
- From inside repo root (`/home/ink/Downloads/local_dashboard`):
  `PYTHONPATH=/home/ink/Downloads python3 -m local_dashboard`

### Lint / static checks
No linter config is present (`ruff`, `flake8`, `pylint`, `mypy` are not configured).
- Syntax-check all Python files: `python3 -m compileall .`
- Optional package import check: `PYTHONPATH=/home/ink/Downloads python3 -c "import local_dashboard"`

If you add tooling, also document it in this file and `README.md`.

### Tests
No test suite currently exists (`tests/` and pytest config are absent).

When tests are added, use these conventions:
- Run all tests: `python3 -m pytest`
- Run one file: `python3 -m pytest tests/test_battery.py`
- Run one test (single-test command):
  `python3 -m pytest tests/test_battery.py::test_estimate_time_remaining`
- Run by pattern: `python3 -m pytest -k conservation`

Prefer focused unit tests for pure logic in `battery.py` and `procs.py`.

## Code Style Guidelines
Preserve current style and behavior patterns unless task requirements say otherwise.

### Python version and dependencies
- Target Python 3.10+ style (`X | None`, builtin generics like `list[dict]`).
- Keep backend stdlib-only unless explicitly requested.
- Avoid new dependencies for small utilities.

### Imports
- Order imports by group:
  1) Python stdlib
  2) local package imports (`from . import ...`, `from .module import ...`)
- Prefer explicit relative imports inside package modules.
- Keep imports minimal; remove unused imports.
- Avoid wildcard imports.

### Formatting
- Use 4-space indentation; no tabs.
- Match surrounding style before reformatting untouched code.
- Keep lines readable; avoid overly compressed one-liners.
- Use trailing commas in multiline literals where helpful for diffs.
- Keep compact style in tight telemetry paths if existing code is already compact.

### Types and signatures
- Add type hints on new or changed functions.
- Keep return types explicit, especially optional returns.
- Prefer concrete containers when obvious (`list[dict]`, `tuple[float, bool]`).
- Represent unavailable telemetry as `None`, not magic values.

### Naming
- Constants: `UPPER_SNAKE_CASE`.
- Functions/variables: `snake_case`.
- Internal helpers: prefix `_`.
- Internal classes/dataclasses may be private (e.g., `_ProcSnap`).
- Favor domain-specific names (`conservation_mode`, `sample_seconds`, `eta`).

### Error handling and resilience
- This codebase is fail-soft for `/proc` and `/sys` reads.
- In samplers/telemetry reads, catch exceptions and continue operating.
- Return `None` or empty structures when telemetry is unavailable.
- For startup-critical issues (e.g., missing battery path), fail fast with clear text.
- Do not let transient hardware/procfs errors crash the HTTP service.

### Concurrency and shared state
- Protect shared mutable buffers with locks.
- Access `battery.DATA` under `battery.LOCK` when reading/copying/mutating.
- Keep background thread targets exception-safe and side-effect-aware.

### API and JSON behavior
- Keep response shapes stable (`available`, `enabled`, `ok`, etc.).
- Use UTF-8 JSON with consistent content type.
- Preserve `Cache-Control: no-store` for live telemetry endpoints.
- Avoid renaming frontend-consumed fields without a migration plan.

### Frontend (`template.py`)
- Keep UI fully offline-capable; local static assets are the default.
- Preserve IBM Plex typography and industrial visual language unless asked to redesign.
- Keep JS simple and framework-light; avoid introducing a frontend build pipeline.
- Keep polling intervals and API wiring easy to trace in plain JS.
- Verify mobile-safe layout behavior after UI changes.

### Config and environment
- Centralize env-derived defaults and paths in `config.py`.
- Add new tunables as env vars with sensible defaults.
- Keep systemd defaults aligned with `README.md`.

### Makefile / ops changes
- Keep install/uninstall targets idempotent.
- Keep helper targets (`logs`, `status`, `restart`) simple and reliable.
- Document operational command changes in both `README.md` and this file.

## Cursor / Copilot Rule Files
Checked for additional agent instructions in:
- `.cursor/rules/`
- `.cursorrules`
- `.github/copilot-instructions.md`

No Cursor or Copilot instruction files were found in this repository.

## Agent Workflow Notes
- Before major edits, inspect `README.md`, `Makefile`, and touched modules.
- Prefer minimal diffs; avoid broad refactors unless required.
- Preserve offline-first behavior.
- If you add tests or tooling, update this file immediately.
