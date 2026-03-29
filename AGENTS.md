# Contributor Guide

This project is a Python 3.12 backend service built with FastMCP and httpx. All source code lives under `src/intervals_mcp_server` and tests live under `tests`.

## Fork Maintenance
- This repository is now maintained as an independent fork.
- Treat `fork/main` as the primary base branch for new work.
- Keep `origin` as reference-only unless there is a specific upstream change you want to port manually.

## Development Environment
- Use [uv](https://github.com/astral-sh/uv) to create and manage the virtual environment.
  - `uv venv --python 3.12`
  - `source .venv/bin/activate`
- Sync dependencies including dev extras with `uv sync --all-extras`.
- When editing or running the server manually use `mcp run src/intervals_mcp_server/server.py`.
- Prefer `uv run ...` for repo-local commands so the checked-in environment and lockfile stay aligned.

## Testing Instructions
- Run unit tests with `uv run pytest` from the repository root.
- Ensure linting passes with `uv run ruff check .`.
- Run static type checks using `uv run mypy src tests`.
- All three steps (`ruff`, `mypy`, and `pytest`) should succeed before committing.

## Versioning And Releases
- The package version lives in `pyproject.toml` and must be kept in sync with `uv.lock`.
- Behavior changes, new tools, new configuration surface, or externally visible fixes should bump the package version before merge.
- Prefer semantic versioning:
  - patch: backward-compatible fixes and internal-only cleanup
  - minor: backward-compatible new tools, diagnostics, or features
  - major: breaking tool, config, or transport changes
- The MCP metadata tools (`get_server_version` and `get_server_info`) should reflect the checked-in package version after your changes.

## PR Instructions
- Use concise commit messages.
- Title pull requests using the format `[intervals-mcp-server] <brief description>`.
- Describe any manual testing steps performed and mention whether `pytest`, `ruff`, and `mypy` passed.

There is currently no frontend code in this repository. If a frontend is added in the future (for example with React or another framework), document how to run and test it within this file.
