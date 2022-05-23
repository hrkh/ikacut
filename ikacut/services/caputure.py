import logging

import cv2
from pendulum.duration import Duration


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
        self, target_image: cv2.Mat, template_image: cv2.Mat, threshold: float
    ) -> bool:
        _, max_val, _, _ = cv2.minMaxLoc(
            cv2.matchTemplate(target_image, template_image, cv2.TM_CCOEFF_NORMED)
        )
        logger.debug("max_val=%f", max_val)

        return max_val >= threshold
