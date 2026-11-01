import click
from rich.console import Console
from shared import cli
from tui.app import main as tuiapplication

console = Console()


@cli.command("tuiapp")
@click.pass_context
def tuiapp(ctx):
    """Monitor network and devices"""
    return tuiapplication()


# @cli.group()
# def tuiapp():
#     """Monitor network and devices"""
#     return
#
#
# @tuiapp.command("tui")
# @click.pass_context
# def start(ctx):
#     return tuiapplication()
