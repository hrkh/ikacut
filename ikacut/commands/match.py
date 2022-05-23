import dataclasses
import logging
import sys
import typing

import click
import cv2
from pendulum.duration import Duration

from ikacut.exceptions import ReadImageError


logger = logging.getLogger(__file__)
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
del logging


@dataclasses.dataclass
class Match:
    match_no: int
    start_time: Duration
    end_time: typing.Optional[Duration]

    @staticmethod
    def format_duration(duration: Duration) -> str:
        elements = []
        if duration.hours > 0:
            elements.append(str(duration.hours))
        elements.append(format(duration.minutes, "02"))
        elements.append(format(duration.remaining_seconds, "02"))

        return ":".join(elements)

    def format_start_time(self) -> str:
        return self.format_duration(self.start_time)

    def format_end_time(self) -> str:
        if self.end_time is None:
            return ""
        return self.format_duration(self.end_time)


def read_image(source: str) -> cv2.Mat:
    image = cv2.imread(source)
    logger.debug("Successfully read the image of starting match")

    return image


def video_info(capture: cv2.VideoCapture) -> typing.Tuple[float, float, float]:
    fps = capture.get(cv2.CAP_PROP_FPS)
    logger.info("fps=%f", fps)
    all_frames = capture.get(cv2.CAP_PROP_FRAME_COUNT)
    logger.info("all_frames=%f", all_frames)
    total_time = all_frames / fps
    logger.info("total_time=%f", total_time)

    return fps, all_frames, total_time


def match_template(
    target_image: cv2.Mat, template_image: cv2.Mat, threshold: float
) -> bool:
    _, max_val, _, _ = cv2.minMaxLoc(
        cv2.matchTemplate(target_image, template_image, cv2.TM_CCOEFF_NORMED)
    )
    logger.debug("max_val=%f", max_val)
    return max_val >= threshold


def calculate_start_time(
    capture: cv2.VideoCapture, fps: float, skip_sec: float
) -> Duration:
    start_frame = capture.get(cv2.CAP_PROP_POS_FRAMES)
    start_time = Duration(seconds=start_frame / fps - skip_sec)

    return start_time


def calculate_end_time(capture: cv2.VideoCapture, fps: float) -> Duration:
    end_frame = capture.get(cv2.CAP_PROP_POS_FRAMES)
    end_time = Duration(seconds=end_frame / fps)

    return end_time


def extract_matches(
    filename: str, first_math_no: int, skip_sec: float, threshold: float
) -> typing.List[Match]:
    capture = cv2.VideoCapture(filename)
    fps, _, total_time = video_info(capture)
    start_image = read_image("./images/start.png")
    end_image = read_image("./images/end.png")

    matches = []
    match_no = first_math_no
    is_in_match = False
    start_time, end_time = None, None
    for i in range(int(total_time / skip_sec)):
        target_msec = i * 1000 * skip_sec
        capture.set(cv2.CAP_PROP_POS_MSEC, target_msec)
        logger.debug("target_msec=%f", target_msec)

        ok, image = capture.read()
        if not ok:
            raise ReadImageError("Failed to read a image from capture")

        if is_in_match:
            is_end_of_match = match_template(image, end_image, threshold)
            if not is_end_of_match:
                continue

            is_in_match = False
            end_time = calculate_end_time(capture, fps)
            logger.info("match_no=%d, end_time='%s'", match_no, end_time)
        else:
            is_start_of_match = match_template(image, start_image, threshold)
            if not is_start_of_match:
                continue

            is_in_match = True
            start_time = calculate_start_time(capture, fps, skip_sec)
            logger.info("match_no=%d, start_time='%s'", match_no, start_time)

        if start_time is None or end_time is None:
            continue
        match = Match(match_no, start_time, end_time)
        matches.append(match)
        match_no += 1
        start_time, end_time = None, None
    if start_time is not None:
        match = Match(match_no, start_time, end_time)
        matches.append(match)
    capture.release()

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
        matches = extract_matches(filename, first_match_no, skip_sec, threshold)
        for match in matches:
            print(
                f"No.{match.match_no}",
                match.format_start_time(),
                "~",
                match.format_end_time(),
            )
