import click

from . import download, match


def add_commands(cli: click.Group):
    download.add_command(cli)
    match.add_command(cli)
