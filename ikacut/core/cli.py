import logging
import sys

import click


logging.basicConfig(stream=sys.stderr, level=logging.INFO)


@click.group()
def cli():
    pass


def main():
    from ikacut import commands

    commands.add_commands(cli)
    cli()
