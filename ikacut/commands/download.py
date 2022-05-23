import click
import yt_dlp

from ikacut.exceptions import YouTubeDownloadError


def download_from_youtube(source_url: str, output_dir: str, filename: str) -> None:
    source_url = [source_url]
    options = {
        "format": "best",
        "paths": {"home": output_dir},
        "outtmpl": f"{filename}.mp4",
        "overwrites": True,
    }
    with yt_dlp.YoutubeDL(options) as ydl:
        result = ydl.download(source_url)
        if result != 0:
            raise YouTubeDownloadError("Failed to download the video file")

def add_command(group: click.Group) -> None:
    @group.command("download")
    @click.argument("source_url", type=str)
    @click.option("-o", "--output-dir", type=str, default="tmp")
    @click.option("-f", "--filename", type=str, default="tmp")
    @click.pass_context
    def command(ctx: click.Context, source_url: str, output_dir: str, filename: str):
        download_from_youtube(source_url, output_dir, filename)
