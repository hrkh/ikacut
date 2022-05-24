import click

from ikacut.services.caputure import IkaCaptureProcessor


def add_command(group: click.Group) -> None:
    @group.command("snapshot")
    @click.argument("target_sec", type=int)
    @click.option("-s", "--source", type=str, default="tmp/tmp.mp4")
    @click.option("-d", "--destination", type=str, default="tmp/tmp.png")
    @click.pass_context
    def command(
        ctx: click.Context,
        target_sec: int,
        source: str,
        destination: str,
    ):
        processor = IkaCaptureProcessor(source)
        processor.snapshot(destination, target_sec)
