"""Maintenance actions exposed by the CLI."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Callable, Iterable

from . import config
from .system import (
    ensure_directory,
    get_local_ipv4,
    open_path,
    open_url,
    run_command,
    run_powershell,
    service_start,
    set_clipboard_text,
    startup_automatic,
    startup_manual,
)


ActionHandler = Callable[[], str | None]


@dataclass(frozen=True)
class ActionSpec:
    key: str
    label: str
    description: str
    needs_admin: bool
    handler: ActionHandler


def create_restore_point() -> str | None:
    run_powershell(
        f'Checkpoint-Computer -Description "{config.SYSTEM_RESTORE_DESCRIPTION}" -RestorePointType "MODIFY_SETTINGS"'
    )
    return None


def open_system_restore() -> str | None:
    run_command(["rstrui.exe"])
    return None


def set_services_manual() -> str | None:
    for service_name in config.MANUAL_SERVICES:
        startup_manual(service_name)
    return None


def disable_defender() -> str | None:
    run_powershell("Set-MpPreference -DisableRealtimeMonitoring $true")
    return None


def enable_defender() -> str | None:
    run_powershell("Set-MpPreference -DisableRealtimeMonitoring $false")
    return None


def disable_firewall() -> str | None:
    run_command(["netsh", "advfirewall", "set", "allprofiles", "state", "off"])
    return None


def enable_firewall() -> str | None:
    run_command(["netsh", "advfirewall", "set", "allprofiles", "state", "on"])
    return None


def enable_network_discovery() -> str | None:
    run_command(
        [
            "netsh",
            "advfirewall",
            "firewall",
            "set",
            "rule",
            'group="Network Discovery"',
            "new",
            "enable=Yes",
        ]
    )
    return None


def full_network_sharing() -> str | None:
    run_powershell("Get-NetConnectionProfile | Set-NetConnectionProfile -NetworkCategory Private")
    enable_network_discovery()
    run_command(
        [
            "netsh",
            "advfirewall",
            "firewall",
            "set",
            "rule",
            'group="File and Printer Sharing"',
            "new",
            "enable=Yes",
        ]
    )
    for service_name in config.NETWORK_SHARING_SERVICES:
        startup_automatic(service_name)
        service_start(service_name)
    run_command(["wmic", "nicconfig", "where", "(IPEnabled=TRUE)", "call", "SetTcpipNetbios", "1"])
    return None


def create_shared_folder() -> str | None:
    path = ensure_directory(config.NETWORK_SHARE_PATH)
    run_powershell(
        f'New-SmbShare -Name "{config.NETWORK_SHARE_NAME}" -Path "{path}" -FullAccess "Everyone" -ErrorAction SilentlyContinue'
    )
    open_path(str(path))
    return None


def show_ip() -> str:
    return f"IP do computador: {get_local_ipv4()}"


def open_network_share() -> str | None:
    open_path(config.DEFAULT_BROWSER_TARGET)
    return None


def copy_network_path() -> str:
    computer_name = os.environ.get("COMPUTERNAME", "")
    value = f"{config.DEFAULT_NETWORK_PATH_PREFIX}{computer_name}"
    set_clipboard_text(value)
    return value


def enable_ultra_performance() -> str | None:
    run_command(["powercfg", "-duplicatescheme", config.EVENT_POWER_SCHEME])
    run_command(["powercfg", "-setactive", config.EVENT_POWER_SCHEME])
    return None


def run_sfc() -> str | None:
    run_command(["cmd", "/c", "sfc /scannow"])
    return None


def run_chkdsk() -> str | None:
    run_command(["cmd", "/c", "chkdsk C: /f /r"])
    return None


def disk_cleanup() -> str | None:
    run_command(["cleanmgr.exe"])
    return None


def update_all_winget() -> str | None:
    run_command(
        [
            "winget",
            "upgrade",
            "--all",
            "--accept-source-agreements",
            "--accept-package-agreements",
        ]
    )
    return None


def disable_background_apps() -> str | None:
    run_command(
        [
            "reg",
            "add",
            r"HKCU\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications",
            "/v",
            "GlobalUserDisabled",
            "/t",
            "REG_DWORD",
            "/d",
            "1",
            "/f",
        ]
    )
    return None


def open_google_drive() -> str | None:
    open_url(config.GOOGLE_DRIVE_URL)
    return None


def open_github_repo() -> str | None:
    open_url(config.GITHUB_REPO_URL)
    return None


def event_mode() -> str | None:
    create_restore_point()
    set_services_manual()
    disable_defender()
    disable_firewall()
    enable_ultra_performance()
    return None


def restore_defaults() -> str | None:
    enable_defender()
    enable_firewall()
    run_command(["powercfg", "-setactive", "SCHEME_BALANCED"])
    for service_name in config.MANUAL_SERVICES:
        startup_automatic(service_name)
    return None


def _service_specs() -> Iterable[ActionSpec]:
    return (
        ActionSpec("restore-point", "Criar Ponto de Restauracao", "Cria um restore point antes de alterar o sistema.", True, create_restore_point),
        ActionSpec("open-system-restore", "Abrir Restauracao do Sistema", "Abre o assistente do Windows para restauracao.", False, open_system_restore),
        ActionSpec("manual-services", "Servicos em Manual", "Coloca SysMain e DiagTrack em manual.", True, set_services_manual),
        ActionSpec("disable-defender", "Desabilitar Defender", "Desativa a monitoracao em tempo real.", True, disable_defender),
        ActionSpec("enable-defender", "Reabilitar Defender", "Reativa a monitoracao em tempo real.", True, enable_defender),
        ActionSpec("disable-firewall", "Desabilitar Firewall", "Desliga os perfis de firewall.", True, disable_firewall),
        ActionSpec("enable-firewall", "Reabilitar Firewall", "Liga os perfis de firewall.", True, enable_firewall),
        ActionSpec("network-discovery", "Ativar Descoberta de Rede", "Habilita regras de descoberta de rede.", True, enable_network_discovery),
        ActionSpec("full-network-sharing", "Compartilhamento de Rede Completo", "Configura rede privada, compartilhamento e servicos.", True, full_network_sharing),
        ActionSpec("create-share", "Criar Pasta Compartilhada", "Cria a pasta e o share SMB BelmonteShare.", True, create_shared_folder),
        ActionSpec("show-ip", "Mostrar IP", "Exibe o IP IPv4 principal.", False, show_ip),
        ActionSpec("open-network-share", "Abrir Compartilhamento na Rede", "Abre \\\\localhost no Explorer.", False, open_network_share),
        ActionSpec("copy-network-path", "Copiar Caminho de Rede", "Copia o caminho \\\\COMPUTERNAME para a area de transferencia.", False, copy_network_path),
        ActionSpec("ultra-performance", "Modo Ultra Desempenho", "Ativa o plano de energia ultra performance.", True, enable_ultra_performance),
        ActionSpec("sfc", "Executar SFC /SCANNOW", "Executa System File Checker.", True, run_sfc),
        ActionSpec("chkdsk", "Executar CHKDSK /R", "Executa verificacao do disco C:.", True, run_chkdsk),
        ActionSpec("disk-cleanup", "Limpeza de Disco", "Abre o utilitario de limpeza de disco.", False, disk_cleanup),
        ActionSpec("winget-update", "Atualizar Tudo via Winget", "Executa upgrade de todos os pacotes.", False, update_all_winget),
        ActionSpec("disable-background-apps", "Desabilitar Apps em Segundo Plano", "Desliga apps em segundo plano do usuario atual.", False, disable_background_apps),
        ActionSpec("open-drive", "Abrir Google Drive Belmonte", "Abre a pasta do Google Drive configurada.", False, open_google_drive),
        ActionSpec("open-github", "Abrir Repositorio no GitHub", "Abre o repositorio Belmonte-Tools no navegador.", False, open_github_repo),
        ActionSpec("event-mode", "MODO EVENTO COMPLETO", "Aplica o pacote de ajustes para evento.", True, event_mode),
        ActionSpec("restore-defaults", "Restaurar Configuracoes Padrao Windows", "Reverte as configuracoes principais.", True, restore_defaults),
    )


ACTION_SPECS = tuple(_service_specs())
ACTION_BY_KEY = {spec.key: spec for spec in ACTION_SPECS}

