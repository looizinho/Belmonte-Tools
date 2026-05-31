# BelmonteTools Migration Plan

## Goal
Port the current PowerShell-based maintenance launcher to Python so it can be shipped first as a CLI executable and later extended with a graphical interface.

## Current Progress
- Python package scaffold created under `src/belmonte_tools`.
- CLI entry point added with one command per maintenance action.
- Legacy `.cmd` launcher redirected to the Python CLI.

## Current State
The repository now contains the legacy PowerShell implementation and a Python CLI scaffold. The PowerShell script remains available as the reference implementation while the Python side becomes the new execution path.

The PowerShell script currently provides:
- A Windows Forms UI with buttons for maintenance actions.
- System restore and recovery entry points.
- Service, firewall, Defender, network discovery, SMB sharing, and power profile changes.
- Convenience actions such as opening folders, showing the local IP, copying the network path, and launching external tools.

## Migration Principles
- Keep the first Python version functionally equivalent to the current tool.
- Separate command logic from UI logic from day one.
- Prefer standard library modules first, and add third-party dependencies only where Windows APIs require it.
- Treat privileged actions as explicit, auditable operations.
- Make the CLI the source of truth so the future GUI only wraps the same action layer.

## Target Architecture

### 1. Core action layer
Create a Python package that exposes one function per maintenance action.

Suggested layout:
- `belmonte_tools/`
- `belmonte_tools/actions/`
- `belmonte_tools/ui/`
- `belmonte_tools/cli.py`
- `belmonte_tools/config.py`
- `belmonte_tools/logging.py`

Responsibilities:
- `actions/`: system operations, each isolated and testable.
- `cli.py`: argument parsing and command dispatch.
- `ui/`: future GUI entry point, initially empty or minimal.
- `config.py`: constants such as paths, URLs, service lists, and restore point names.

### 2. CLI first
The Python executable should expose:
- A `list` command to show available actions.
- One command per action.
- A `run-all` or profile command for combined workflows such as event mode or full network sharing.
- Clear output, return codes, and logging suitable for troubleshooting.

### 3. GUI later
After the CLI is stable, add a GUI layer that only calls the same action functions.
That keeps the business logic reusable and avoids a second implementation of every maintenance task.

## Command Inventory

The current PowerShell script contains the following action groups:

### Safe or low-risk convenience actions
- Open System Restore.
- Open a shared folder in Explorer.
- Show the local IP address.
- Copy the computer network path.
- Open a Google Drive folder.
- Launch Disk Cleanup.

### Elevated or high-risk system actions
- Create a restore point.
- Set services to manual or automatic.
- Disable or re-enable Defender real-time monitoring.
- Disable or enable firewall profiles.
- Enable network discovery and file sharing.
- Create an SMB share.
- Change the network category to Private.
- Enable NetBIOS over TCP/IP.
- Set the ultra performance power plan.
- Run SFC.
- Run CHKDSK.
- Trigger Winget upgrade all.
- Disable background apps.
- Set the event mode bundle.
- Restore Windows defaults.

## Suggested Python Implementation Strategy

### Phase 1. Inventory and parity
Before rewriting, map every PowerShell button to:
- Exact command sequence.
- Whether admin rights are required.
- Whether the action is idempotent.
- Whether it can fail harmlessly.
- Whether it needs user confirmation.

Deliverable:
- A command matrix in code or documentation.

### Phase 2. Build the action layer
Implement the system operations in Python using the smallest practical dependency set.

Likely tools:
- `subprocess` for native commands such as `rstrui.exe`, `powercfg`, `netsh`, `sfc`, `chkdsk`, `winget`, `cleanmgr`, and `reg`.
- `ctypes` or `pywin32` for Windows-specific APIs where needed.
- `psutil` for network and process inspection if needed.
- `winreg` for registry writes.
- `socket` or `psutil` for IP display logic.
- `logging` for structured logs.

Important behavior to preserve:
- Actions should not silently swallow failures.
- Dangerous actions should ask for confirmation in CLI mode.
- Commands that require elevation should detect that early and explain why.

### Phase 3. CLI executable
Build a command-line interface around the action layer.

Recommended CLI behavior:
- `belmonte-tools --help`
- `belmonte-tools list`
- `belmonte-tools restore-point`
- `belmonte-tools disable-firewall`
- `belmonte-tools event-mode`

Recommended user experience:
- Use short, descriptive command names.
- Print a success or failure summary after each action.
- Exit with non-zero status codes on failure.

### Phase 4. Packaging
Package the CLI into a Windows executable.

Recommended approach:
- Start with PyInstaller for the fastest path to a distributable `.exe`.
- Add a build script that pins version, icon, and output folder.
- Keep the Python source layout compatible with future GUI packaging.

### Phase 5. GUI foundation
Once the CLI is stable:
- Introduce a GUI framework such as Tkinter, PySide6, or another Windows-friendly toolkit.
- Reuse the same action layer.
- Keep GUI widgets thin and declarative.
- Avoid embedding shell commands inside the UI layer.

## Suggested Implementation Order
1. Recreate the action inventory in Python.
2. Implement helper utilities for elevation, logging, and command execution.
3. Port the least risky actions first.
4. Port the shared network and power-profile workflows.
5. Port the elevated system-changing actions.
6. Add CLI argument parsing and help text.
7. Add packaging for a single-file executable.
8. Add GUI only after CLI parity is acceptable.

## Risk Areas

### Privilege and elevation
Many actions require administrator rights. The Python version should detect elevation status and either self-elevate or fail with a clear message.

### Windows-only behavior
The project is tightly tied to Windows APIs and command-line tools. The Python version should explicitly state that it targets Windows only.

### Side effects
Some current actions modify firewall, Defender, services, and network sharing settings. These need:
- explicit confirmation,
- clear rollback paths where possible,
- and careful logging.

### Command compatibility
Some PowerShell cmdlets do not have direct one-to-one Python replacements. In those cases, call the underlying Windows tool rather than trying to reimplement the system feature.

## Recommended Quality Gates
- Each action can be run independently from the CLI.
- Each action reports success/failure clearly.
- Event mode and restore-default mode behave as opposite pairs.
- Administrative actions fail gracefully when not elevated.
- Packaging produces a working executable on a clean Windows machine.
- Manual smoke test covers every button-equivalent command.

## Open Questions To Decide Early
- Which GUI toolkit should be used later.
- Whether the CLI should self-elevate or require the user to launch as admin.
- Whether to keep the existing `.cmd` wrapper for compatibility or replace it with a Python launcher.
- Whether to preserve the current Portuguese labels or move to bilingual naming.

## Short Recommendation
The safest path is:
- Python action layer first.
- CLI second.
- Packaging third.
- GUI last.

That order minimizes rewrite risk and lets us validate the system-changing commands before adding interface complexity.
