# Repository Guidelines

## Project Structure & Module Organization
- `BelmonteTools.ps1` is the main application script. It builds the Windows Forms UI and wires each maintenance action to a button.
- `BelmonteTools.cmd` is the recommended entry point for end users; it launches PowerShell with `-ExecutionPolicy Bypass` and hides the window.
- `mise.toml` pins local tooling preferences. `venv/` is a checked-in Python environment and should be treated as tooling-only, not product code.

## Build, Test, and Development Commands
- `.\BelmonteTools.cmd` launches the app the same way a user would.
- `powershell -ExecutionPolicy Bypass -File .\BelmonteTools.ps1` runs the script directly during development.
- `mise` is available for tool management if you need the configured Node runtime, but there is no separate build pipeline in this repository.

## Coding Style & Naming Conventions
- Use PowerShell conventions: `PascalCase` for functions and cmdlets, clear verb-noun names where possible, and descriptive variable names.
- Keep indentation consistent within blocks; use 4 spaces for nested script blocks and align related statements vertically when it improves readability.
- Prefer double-quoted strings when interpolation is needed, and keep button labels short, user-facing, and action-oriented.

## Testing Guidelines
- There is no automated test suite in the current repository.
- Validate changes manually by opening the app and clicking the affected buttons.
- For risky actions, verify the command path carefully before shipping, especially entries that change firewall, Defender, services, or power settings.

## Commit & Pull Request Guidelines
- No Git history is available in this checkout, so no repository-specific commit convention can be confirmed here.
- Use short, imperative commit subjects such as `Add restore-point button` or `Refine network sharing flow`.
- Pull requests should explain what changed, how it was tested, and include screenshots for UI updates or notes for any system-level side effects.

## Security & Configuration Tips
- This tool makes privileged system changes. Review commands before running them on a real machine.
- Avoid hard-coding machine-specific paths unless the action is intentionally tied to the local workstation.
