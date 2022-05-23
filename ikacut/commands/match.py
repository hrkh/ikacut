import dataclasses
import logging
import typing

import click
import cv2
from pendulum.duration import Duration

from ikacut.exceptions import ReadImageError
from ikacut.services.caputure import IkaCaptureProcessor


logger = logging.getLogger(__file__)
del logging


@dataclasses.dataclass
class Match:
    match_no: int
    start_time: Duration
    end_time: typing.Optional[Duration]

    def format_start_time(self) -> str:
        return self.format_duration(self.start_time)

    def format_end_time(self) -> str:
        if self.end_time is None:
            return ""
        return self.format_duration(self.end_time)


class MatchesExtractor(IkaCaptureProcessor):
    def __init__(
        self, filename: str, first_match_no: int, skip_sec: float, threshold: float
    ) -> None:
        super().__init__(filename)
        self.first_match_no = first_match_no
        self.skip_sec = skip_sec
        self.threshold = threshold

    def extract(self) -> typing.List[Match]:
        matches = []
        match_no = self.first_match_no
        is_in_match = False
        start_time, end_time = None, None

        start_image = self.read_image("./images/start.png")
        end_image = self.read_image("./images/end.png")

        for i in range(int(self.total_time / self.skip_sec)):
            target_msec = i * 1000 * self.skip_sec
            self.capture.set(cv2.CAP_PROP_POS_MSEC, target_msec)
            logger.debug("Set: target_msec=%f", target_msec)

            ok, image = self.capture.read()
            if not ok:
                raise ReadImageError("Failed to read a image from capture")

            if is_in_match:
                is_end_of_match = self.match_template(image, end_image, self.threshold)
                if not is_end_of_match:
                    continue
                is_in_match = False
                end_time = self.calculate_time()
                logger.info("Matched: match_no=%d, end_time='%s'", match_no, end_time)
            else:
                is_start_of_match = self.match_template(
                    image, start_image, self.threshold
                )
                if not is_start_of_match:
                    continue
                is_in_match = True
                start_time = self.calculate_time(rewind_sec=self.skip_sec)
                logger.info(
                    "Matched: match_no=%d, start_time='%s'", match_no, start_time
                )


            if start_time is None or end_time is None:
                continue

            match = Match(match_no, start_time, end_time)
            matches.append(match)
            match_no += 1
            start_time, end_time = None, None

        if start_time is not None:
            match = Match(match_no, start_time, end_time)
            matches.append(match)

        return matches


def add_command(group: click.Group) -> None:
    @group.command("match")
    @click.option("-f", "--filename", type=str, default="tmp/tmp.mp4")
    @click.option("-n", "--first-match-no", type=int, default=1)
    @click.option("-s", "--skip-sec", type=float, default=3.0)
    @click.option("-t", "--threshold", type=float, default=0.9)
    @click.pass_context
    def command(
        ctx: click.Context,
        filename: str,
        first_match_no: int,
        skip_sec: float,
        threshold: float,
    ):
        extractor = MatchesExtractor(filename, first_match_no, skip_sec, threshold)
        matches = extractor.extract()
        for match in matches:
            print(
                f"No.{match.match_no}",
                match.format_start_time(),
                "~",
                match.format_end_time(),
            )
