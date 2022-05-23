import click

from . import death, download, match


def add_commands(cli: click.Group):
    death.add_command(cli)
    download.add_command(cli)
    match.add_command(cli)
