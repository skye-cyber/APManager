from rich.console import Console
from rich.panel import Panel
from ap_utils.config import config_manager
from core.shared import shared as sharedlib

console = Console()


def statsFn(progress_fn):
    try:
        config = config_manager.get_config

        dnsamasq_pid = None
        hostapd_pid = None
        with open(config_manager.dnsmasq_pidfile.as_posix(), "r") as f:
            dnsamasq_pid = f.read()
            dnsamasq_pid = dnsamasq_pid.strip() if dnsamasq_pid else dnsamasq_pid
        with open(config_manager.hostapd_pidfile.as_posix(), "r") as f:
            hostapd_pid = f.read()
            hostapd_pid = hostapd_pid.strip() if hostapd_pid else hostapd_pid

    except Exception as e:
        progress_fn("Hotspot process errored")
        console.print(f"[red]Error: {e}[/red]")
        return

    console.print(
        Panel.fit(
            "[bold green]✓ Hotspot started successfully![/bold green]\n\n"
            f"[cyan]SSID:[/cyan] {config['ssid'] or 'From config'}\n"
            f"[cyan]AP Interface[/cyan] {config['vwifi_iface']}\n"
            f"[cyan]Net Interface:[/cyan] {config['internet_iface']}\n"
            f"[cyan]Sharing Method:[/cyan] {config['share_method']}\n"
            f"[cyan]DNSMASQ PID:[/cyan] {dnsamasq_pid or '-'}\n"
            f"[cyan]HOSTAPD PID:[/cyan] {hostapd_pid or '-'}\n",
            title="AccessPoint Status",
        )
    )


def sysExFn(code, retries, progress_fn, start_fn, prevChannel):
    if code != 0:
        # Retry with fixed channel: channel for the currently connected wifi
        channel = sharedlib.get_current_channel()
        if retries == 0 and channel:
            retries += 1
            print(f"\nSwitch channel from: {prevChannel} to: {channel}\n")
            progress_fn(
                f"[Retry] [green]Channel {channel}[/green]",
            )
            # Sync channel and save
            config_manager.set("channel", channel)
            return start_fn()

        progress_fn("APManager startup exited unexpectedly")
        console.print(
            Panel.fit(
                "[bold red]✗ Hotspot failed to start[/bold red]\n\n"
                "The startup routine exited before the hotspot came up "
                f"(exit code [yellow]{code}[/yellow]).\n"
                # "Check the logs, service permissions, and that no other "
                # "AP/hostapd/dnsmasq instance is already running.\n"
                f"Ensure channel [green]{prevChannel}[/green] in config matches wifi interface channel",
                title="Startup Failed",
            )
        )
        raise  # preserve original exit behavior for the caller
