# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

- **Install editable package**: `pip install -e .` (runs in the repository root)
- **Run the CLI**: `belmonte-tools <command>`
- **Show help**: `belmonte-tools --help` or `belmonte-tools <subcommand> --help`
- **List available actions**: `belmonte-tools list`
- **Execute a specific maintenance action**: `belmonte-tools <action-key>` (e.g., `belmonte-tools event-mode`)
- **Run unit tests**: *(none provided – add tests under a `tests/` folder and run `pytest` when they exist)*
- **Linting**: `ruff .` or `flake8 .` (if lint tools are installed)
- **Build wheel**: `python -m build`

## High‑Level Architecture

- **Entry point (`src/belmonte_tools/cli.py`)** – Parses command‑line arguments with `argparse` and dispatches to actions.
- **Action registry (`src/belmonte_tools/actions.py`)** – Defines `ActionSpec` dataclass and a collection `ACTION_SPECS` mapping keys to handler functions. Each handler performs a Windows system operation via helpers.
- **Configuration (`src/belmonte_tools/config.py`)** – Central constants for power schemes, network share settings, and service lists.
- **System helpers (`src/belmonte_tools/system.py`)** – Thin wrappers around Windows commands (PowerShell, `sc` service control, `netsh`, clipboard, etc.) and utility functions (`is_admin`, `get_local_ipv4`).
- **Package metadata (`pyproject.toml`)** – Declares the project as a console script `belmonte-tools` pointing to `cli:main`.

The CLI is Windows‑only; many actions require administrator privileges (`is_admin` check). The `event-mode` action illustrates a typical workflow: create a restore point, set services to manual, disable Defender and firewall, and enable an ultra‑performance power plan.

## Extending the Tool

- Add new `ActionSpec` entries in `actions.py` and corresponding handler functions.
- Update `config.py` for any new constant values.
- Ensure any new system commands go through the `run_command`/`run_powershell` helpers for consistent error handling.

## Notes for Claude Code

- When invoking the CLI, prefer the short action keys listed in `ACTION_BY_KEY` (e.g., `event-mode`, `disable-defender`).
- Use the configuration constants from `config.py` rather than hard‑coding literals.
- All system interactions are encapsulated in `system.py`; modifications should respect the existing wrapper patterns.
