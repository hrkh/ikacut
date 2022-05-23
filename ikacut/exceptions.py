class OpenCV2Error(Exception):
    pass


class ReadImageError(OpenCV2Error):
    pass


class YouTubeError(Exception):
    pass


class YouTubeDownloadError(YouTubeError):
    pass
