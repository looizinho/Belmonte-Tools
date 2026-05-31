"""Command line interface for BelmonteTools."""

from __future__ import annotations

import argparse
import sys
from textwrap import dedent

from . import __version__
from .actions import ACTION_BY_KEY, ACTION_SPECS
from .system import is_admin, is_windows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="belmonte-tools",
        description="Ferramenta de manutencao do Windows da Belmonte Audiovisual.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent(
            """
            Exemplos:
              belmonte-tools          (abre o menu interativo)
              belmonte-tools list
              belmonte-tools restore-point
              belmonte-tools event-mode
            """
        ).strip(),
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("list", help="Lista os comandos disponiveis.")
    subparsers.add_parser("menu", help="Abre o menu interativo (padrao quando sem argumentos).")

    for spec in ACTION_SPECS:
        subparsers.add_parser(spec.key, help=spec.description)

    return parser


def _print_actions() -> None:
    for spec in ACTION_SPECS:
        admin_tag = "admin" if spec.needs_admin else "user"
        print(f"{spec.key:24} [{admin_tag}] {spec.label}")


def _execute_action(key: str) -> int:
    if not is_windows():
        print(f"Erro: '{key}' so pode ser executado no Windows.")
        return 1
    spec = ACTION_BY_KEY[key]
    if spec.needs_admin and not is_admin():
        print(f"Erro: '{key}' exige permissao de administrador.")
        return 1
    try:
        result = spec.handler()
    except Exception as exc:  # noqa: BLE001
        print(f"Falha em '{key}': {exc}")
        return 1
    if result:
        print(result)
    else:
        print(f"OK: {spec.label}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # No argument → open interactive menu
    if args.command is None or args.command == "menu":
        from .tui import run_menu
        return run_menu()

    if args.command == "list":
        _print_actions()
        return 0

    if args.command not in ACTION_BY_KEY:
        parser.error(f"Unknown command: {args.command}")

    return _execute_action(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
