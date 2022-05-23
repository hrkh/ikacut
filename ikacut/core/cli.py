import click


@click.group()
def cli():
    pass


def main():
    from ikacut import commands
    commands.add_commands(cli)
    cli()
