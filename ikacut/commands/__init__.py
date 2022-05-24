import click

from . import death, download, match, snapshot


def add_commands(cli: click.Group):
    death.add_command(cli)
    download.add_command(cli)
    match.add_command(cli)
    snapshot.add_command(cli)
