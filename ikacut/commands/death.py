from datetime import datetime
from genericpath import exists
import logging
import os
import subprocess


import click
import cv2
from pendulum.duration import Duration

from ikacut.exceptions import ReadImageError
from ikacut.services.caputure import IkaCaptureProcessor


logger = logging.getLogger(__file__)
del logging


class DeathExtractor(IkaCaptureProcessor):
    def __init__(
        self, filename: str, record_sec: float, skip_sec: float, threshold: float
    ) -> None:
        super().__init__(filename)
        self.filename = filename
        self.record_sec = record_sec
        self.skip_sec = skip_sec
        self.threshold = threshold

    def extract(self):
        death_image = self.read_image("./images/death.png")

        dt = datetime.now().isoformat()
        os.makedirs(f"./data/{dt}", exist_ok=True)

        last_death_time = None
        for i in range(int(self.total_time / self.skip_sec)):
            target_msec = i * 1000 * self.skip_sec
            self.capture.set(cv2.CAP_PROP_POS_MSEC, target_msec)
            logger.debug("Set: target_msec=%f", target_msec)

            ok, image = self.capture.read()
            if not ok:
                raise ReadImageError("Failed to read a image from capture")

            is_death = self.match_template(image, death_image, self.threshold)
            if not is_death:
                continue
            death_time = self.calculate_time(rewind_sec=self.record_sec)
            if last_death_time is not None and death_time - last_death_time < Duration(seconds=10):
                logger.debug("Skipped: death_time='%s'", death_time)
                continue
            last_death_time = death_time
            logger.info("Matched: death_time='%s'", death_time)

            cmd = [
                "ffmpeg",
                "-ss",
                str(int(death_time.total_seconds())),
                "-i",
                self.filename,
                "-t",
                str(int(self.record_sec)),
                "-vcodec",
                "copy",
                "-acodec",
                "copy",
                f"./data/{dt}/{self.format_duration(death_time)}.mp4",
            ]
            subprocess.run(cmd)


def add_command(group: click.Group) -> None:
    @group.command("death")
    @click.option("-f", "--filename", type=str, default="tmp/tmp.mp4")
    @click.option("-r", "--record-sec", type=float, default=30.0)
    @click.option("-s", "--skip-sec", type=float, default=3.0)
    @click.option("-t", "--threshold", type=float, default=0.9)
    @click.pass_context
    def command(
        ctx: click.Context,
        filename: str,
        record_sec: float,
        skip_sec: float,
        threshold: float,
    ):
        extractor = DeathExtractor(filename, record_sec, skip_sec, threshold)
        extractor.extract()
