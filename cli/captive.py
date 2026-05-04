import os
import click
from rich.console import Console
from rich.prompt import Confirm

from shared import cli
from utils.pretyprint import display_captive_info
from Captive.core.manager import CaptiveManager
from Captive.core.config import ConfigManager
from Captive.core.config import configmanager as captiveconfig
from Captive.core.VPN import vpnAuthenticator

console = Console()


@cli.group()
def captive():
    """Captive portal management(Firewall--nat)"""
    pass


@captive.command("enable")
@click.option("--vpn", is_flag=True, help="Do not enable vpn interfaces")
@click.option("--config-file", type=click.Path(exists=True), help="Custom config file")
@click.pass_context
def captive_enable(ctx, vpn, config_file):
    """Start captive and captive portal"""
    config_file = config_file or ctx.obj["config"] or "/etc/ap_manager/conf/config.json"

    with console.status("[bold yellow]Starting captive...\n"):
        try:
            config = ConfigManager(config_file=config_file)
            captive = CaptiveManager(config)
            success = captive.start(vpn=vpn)

            if success:
                console.print("[green]✓ Captive and captive portal started[/green]")
            else:
                console.print("[red]✗ Failed to start captive[/red]")
        except Exception as e:
            raise
            console.print(f"[red]Error: {e}[/red]")


@captive.command("disable")
@click.option("--force", "-f", is_flag=True, help="Force reply yes")
@click.option("--no-vpn", is_flag=True, help="Do not disable vpn interfaces")
@click.option("--config-file", type=click.Path(exists=True), help="Custom config file")
@click.pass_context
def captive_disable(ctx, force, no_vpn, config_file):
    """Disable captive and captive portal"""
    config_file = config_file or ctx.obj["config"] or "/etc/ap_manager/conf/config.json"

    if force or Confirm.ask("Disable captive and captive portal?"):
        with console.status("[bold yellow]Stopping captive..."):
            try:
                config = ConfigManager(config_file=config_file)
                captive = CaptiveManager(config)
                success = captive.stop(novpn=no_vpn)

                if success:
                    console.print("[green]✓ Firewall stopped/disable[/green]")
                else:
                    console.print("[red]✗ Failed to stop/disable captive[/red]")
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")


@captive.command("status")
@click.option("--config-file", type=click.Path(exists=True), help="Custom config file")
@click.pass_context
def captive_status(ctx, config_file):
    """Show captive status"""
    config_file = config_file or ctx.obj["config"]

    try:
        config = (
            ConfigManager(config_file=config_file) if config_file else captiveconfig
        )
        captive = CaptiveManager(config)
        result = captive.status()
        display_captive_info(result)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@captive.command("reset")
@click.option("--no-vpn", is_flag=True, help="Do not reset vpn interface rules")
@click.option("--config-file", type=click.Path(exists=True), help="Custom config file")
@click.pass_context
def captive_reset(ctx, no_vpn, config_file):
    """Reset Captive (stop+resets auth file)"""
    config_file = config_file or ctx.obj["config"]

    try:
        config = (
            ConfigManager(config_file=config_file) if config_file else captiveconfig
        )
        captive = CaptiveManager(config)
        captive.reset(novpn=no_vpn)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@captive.command("vpnon")
@click.option(
    "--interface",
    "-i",
    required=True,
    type=str,
    help="VPN interface(any existing interface)",
)
@click.pass_context
def captive_vpn_enable(ctx, interface):
    """Enable/Allow traffic to/from vpn interface"""
    try:
        return vpnAuthenticator.allowVPNInterface(iface=interface)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@captive.command("vpnoff")
@click.option(
    "--interface",
    "-i",
    required=True,
    type=str,
    help="VPN interface(any existing interface)",
)
@click.pass_context
def captive_vpn_disable(ctx, interface):
    """Disable/Disallow traffic to/from vpn interface"""
    try:
        return vpnAuthenticator.blockVPNInterface(iface=interface)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@captive.command("vpnnon")
@click.option(
    "--interface",
    "-i",
    required=True,
    type=str,
    help="VPN interface(any existing interface)",
)
@click.pass_context
def captive_vpn_reset(ctx, interface):
    """No explit rules for traffic to/from vpn interface"""
    try:
        return vpnAuthenticator.resetVPNInterface(iface=interface)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@captive.command("debug")
@click.option("--config-file", type=click.Path(exists=True), help="Custom config file")
@click.pass_context
def captive_debug(ctx, config_file):
    """Debug Captive and captive portal"""
    config_file = config_file or ctx.obj["config"] or "/etc/ap_manager/conf/config.json"

    with console.status("[bold yellow]Running debug...\n"):
        try:
            config = (
                ConfigManager(config_file=config_file) if config_file else captiveconfig
            )
            captive = CaptiveManager(config)
            captive.debug()
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


@captive.group()
def config():
    """Captive (+captive) Configuration management"""
    pass


@config.command("show")
@click.pass_context
def show_captive_config_(ctx):
    """Show current configuration"""

    if captiveconfig:
        config_data = captiveconfig.get_config()

        console.print("[bold]Current Captive Configuration:[/bold]")
        for key, value in config_data.items():
            if value:  # Skip empty values
                console.print(f"  [cyan]{key}:[/cyan] {value}")
    else:
        console.print("[yellow]No configuration loaded[/yellow]")


@config.command("set")
@click.argument("key")
@click.argument("value")
@click.pass_context
def set_captive_config(ctx, key, value):
    """Set a configuration value"""
    new_conf = captiveconfig._dict_update_config({key: value})
    captiveconfig.save_config()
    captiveconfig.update_config(**new_conf)
    console.print(f"[green]✓ Set {key} = {value}[/green]")


@config.command("edit")
@click.option("--editor", default=None, help="Editor to use")
@click.pass_context
def edit_captive_config(ctx, editor):
    """Edit configuration file with text editor"""

    if captiveconfig:
        config_file = captiveconfig.config_file

        # Use provided editor or default
        editor = editor or os.environ.get("EDITOR", "nano")

        os.system(f"{editor} {config_file}")
        console.print(f"[green]✓ Edited {config_file}[/green]")
    else:
        console.print("[red]No captive configuration file loaded[/red]")
