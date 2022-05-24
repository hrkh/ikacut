import logging
import typing

import cv2
from pendulum.duration import Duration

from ikacut.exceptions import ReadImageError

logger = logging.getLogger(__file__)
del logging


class IkaCaptureProcessor:
    def __init__(self, filename: str) -> None:
        self.capture = cv2.VideoCapture(filename)
        self._fps: float = None
        self._all_frames: float = None
        self._total_time: float = None

    def __del__(self) -> None:
        self.capture.release()

    @staticmethod
    def read_image(source: str) -> cv2.Mat:
        image = cv2.imread(source)
        logger.debug("Successfully read the image of starting match")

        return image

    @staticmethod
    def format_duration(duration: Duration) -> str:
        elements = []
        if duration.hours > 0:
            elements.append(str(duration.hours))
        elements.append(format(duration.minutes, "02"))
        elements.append(format(duration.remaining_seconds, "02"))

        return ":".join(elements)

    @property
    def fps(self) -> float:
        if self._fps is None:
            self._fps = self.capture.get(cv2.CAP_PROP_FPS)
            logger.info("fps=%f", self._fps)
        return self._fps

    @property
    def all_frames(self) -> float:
        if self._all_frames is None:
            self._all_frames = self.capture.get(cv2.CAP_PROP_FRAME_COUNT)
            logger.info("all_frames=%f", self._all_frames)
        return self._all_frames

    @property
    def total_time(self) -> float:
        if self._total_time is None:
            self._total_time = self.all_frames / self.fps
            logger.info("total_time=%f", self._total_time)
        return self._total_time

    def calculate_time(self, rewind_sec: float = 0.0) -> Duration:
        frame = self.capture.get(cv2.CAP_PROP_POS_FRAMES)
        seconds = frame / self.fps - rewind_sec
        time = Duration(seconds=seconds)

        return time

    def match_template(
        self,
        target_image: cv2.Mat,
        template_images: typing.Union[cv2.Mat, typing.List[cv2.Mat]],
        threshold: float,
    ) -> bool:
        if not isinstance(template_images, list):
            template_images = [template_images]
        for template_image in template_images:
            _, max_val, _, _ = cv2.minMaxLoc(
                cv2.matchTemplate(target_image, template_image, cv2.TM_CCOEFF_NORMED)
            )
            logger.debug("max_val=%f", max_val)
            if max_val >= threshold:
                return True
        return False

    def get_image(self) -> cv2.Mat:
        ok, image = self.capture.read()
        if not ok:
            raise ReadImageError("Failed to read a image from capture")
        return image

    def snapshot(self, filename: str, target_sec: int, gray: bool = False) -> None:
        self.capture.set(cv2.CAP_PROP_POS_MSEC, target_sec * 1000)
        image = self.get_image()
        if gray:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(filename, image)
