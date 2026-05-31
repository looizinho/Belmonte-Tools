"""Interactive terminal UI for BelmonteTools (cross-platform)."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from .actions import ACTION_SPECS, ACTION_BY_KEY, ActionSpec
from .system import is_windows, is_admin

console = Console()

BANNER = """
██████╗ ███████╗██╗     ███╗   ███╗ ██████╗ ███╗   ██╗████████╗███████╗
██╔══██╗██╔════╝██║     ████╗ ████║██╔═══██╗████╗  ██║╚══██╔══╝██╔════╝
██████╔╝█████╗  ██║     ██╔████╔██║██║   ██║██╔██╗ ██║   ██║   █████╗
██╔══██╗██╔══╝  ██║     ██║╚██╔╝██║██║   ██║██║╚██╗██║   ██║   ██╔══╝
██████╔╝███████╗███████╗██║ ╚═╝ ██║╚██████╔╝██║ ╚████║   ██║   ███████╗
╚═════╝ ╚══════╝╚══════╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝
"""


def _platform_tag() -> str:
    if is_windows():
        admin = is_admin()
        return f"[bold green]Windows[/bold green] {'[yellow](Admin)[/yellow]' if admin else '[red](Sem Admin)[/red]'}"
    return "[bold cyan]macOS[/bold cyan] [dim](visualizacao — acoes Windows serao bloqueadas)[/dim]"


def _build_table() -> Table:
    table = Table(
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
        expand=True,
        padding=(0, 1),
    )
    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column("Chave", style="bold cyan", min_width=26)
    table.add_column("Descricao", style="white")
    table.add_column("Req.", justify="center", width=6)

    for idx, spec in enumerate(ACTION_SPECS, start=1):
        req = "[red]Admin[/red]" if spec.needs_admin else "[green]User[/green]"
        if not is_windows() and spec.needs_admin:
            row_style = "dim"
        else:
            row_style = ""
        table.add_row(str(idx), spec.key, spec.label, req, style=row_style)

    return table


def _execute(spec: ActionSpec) -> None:
    if not is_windows():
        console.print(
            Panel(
                f"[yellow]A acao '[bold]{spec.key}[/bold]' so pode ser executada no Windows.[/yellow]",
                title="Plataforma incompativel",
                border_style="yellow",
            )
        )
        return

    if spec.needs_admin and not is_admin():
        console.print(
            Panel(
                f"[red]A acao '[bold]{spec.key}[/bold]' requer permissao de Administrador.[/red]",
                title="Permissao insuficiente",
                border_style="red",
            )
        )
        return

    console.print(f"\n[bold]Executando:[/bold] {spec.label}...")
    try:
        result = spec.handler()
        msg = result if result else f"[green]OK:[/green] {spec.label}"
        console.print(Panel(str(msg), border_style="green"))
    except Exception as exc:  # noqa: BLE001
        console.print(Panel(f"[red]Erro:[/red] {exc}", border_style="red"))


def run_menu() -> int:
    while True:
        console.clear()
        console.print(Text(BANNER.strip(), style="bold blue"), justify="center")
        console.print(
            Panel(
                _platform_tag(),
                title="[bold]BelmonteTools[/bold]",
                subtitle="Belmonte Audiovisual",
                border_style="blue",
            )
        )
        console.print(_build_table())
        console.print(
            "\nDigite o [bold cyan]numero[/bold cyan] ou a [bold cyan]chave[/bold cyan] da acao, "
            "ou [bold red]q[/bold red] para sair."
        )

        try:
            raw = console.input("\n[bold]> [/bold]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Saindo...[/dim]")
            return 0

        if raw.lower() in ("q", "quit", "sair", "exit"):
            console.print("[dim]Saindo...[/dim]")
            return 0

        spec: ActionSpec | None = None

        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(ACTION_SPECS):
                spec = ACTION_SPECS[idx]
            else:
                console.print("[red]Numero invalido.[/red]")
        elif raw in ACTION_BY_KEY:
            spec = ACTION_BY_KEY[raw]
        else:
            console.print(f"[red]Opcao desconhecida:[/red] '{raw}'")

        if spec:
            _execute(spec)
            try:
                console.input("\n[dim]Pressione Enter para continuar...[/dim]")
            except (KeyboardInterrupt, EOFError):
                return 0

    return 0
