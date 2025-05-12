"""Custom exceptions for the media service."""

class MediaServiceError(Exception):
    """Base exception for all media service errors."""
    pass

class DownloadError(MediaServiceError):
    """Raised when a download fails."""
    pass

class UnsupportedVideoError(MediaServiceError):
    """Raised when a video cannot be processed due to unsupported format or restrictions."""
    pass

class VideoTooLargeError(MediaServiceError):
    """Raised when a video exceeds the maximum allowed size or duration."""
    pass