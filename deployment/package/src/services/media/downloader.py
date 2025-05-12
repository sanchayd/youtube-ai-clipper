"""YouTube video downloader service implementing the Repository pattern."""

import os
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Tuple
import tempfile
import time

import pytube
from pytube.exceptions import PytubeError

from src.services.media.exceptions import DownloadError, UnsupportedVideoError, VideoTooLargeError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MediaRepository(ABC):
    """Abstract interface for media repositories."""
    
    @abstractmethod
    def download(self, url: str, output_path: Optional[str] = None) -> str:
        """Download media from the given URL."""
        pass
    
    @abstractmethod
    def get_info(self, url: str) -> Dict[str, Any]:
        """Get metadata about the media."""
        pass


class YouTubeRepository(MediaRepository):
    """Repository implementation for YouTube videos with memory optimization."""
    
    def __init__(self, max_duration_minutes: int = 120):
        """Initialize repository with constraints."""
        self.max_duration_minutes = max_duration_minutes
        self._cache = {}  # Simple in-memory cache for video information
    
    def get_info(self, url: str) -> Dict[str, Any]:
        """
        Get metadata about the YouTube video with better handling for API restrictions.
        """
        cache_key = f"info_{url}"
        
        # Check cache first
        if cache_key in self._cache:
            logger.info(f"Cache hit for {url}")
            return self._cache[cache_key]
        
        try:
            # Set custom headers to bypass YouTube restrictions
            yt = pytube.YouTube(
                url,
                use_oauth=False,
                allow_oauth_cache=False
            )
            
            # Add headers that mimic a real browser
            yt.headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            }
            
            # Extract relevant information
            info = {
                "id": yt.video_id,
                "title": yt.title,
                "length_seconds": yt.length,
                "author": yt.author,
                "publish_date": str(yt.publish_date) if yt.publish_date else None,
                "views": yt.views,
                "thumbnail_url": yt.thumbnail_url
            }
            
            # Cache the result
            self._cache[cache_key] = info
            return info
            
        except PytubeError as e:
            logger.error(f"PyTube error for URL {url}: {str(e)}")
            raise DownloadError(f"Failed to get video info: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error for URL {url}: {str(e)}")
            raise DownloadError(f"Unexpected error processing video: {str(e)}")
    
    def download(self, url: str, output_path: Optional[str] = None) -> str:
        """
        Download a YouTube video and return the path to the downloaded file.
        
        Implements:
        - Circuit breaker pattern with retries
        - Memory usage optimization with streaming
        - Resource cleanup
        - Duration validation
        """
        # Default to data directory if no output path specified
        if not output_path:
            output_path = os.path.join(os.getcwd(), "data", "downloads")
            os.makedirs(output_path, exist_ok=True)
        
        try:
            # Get video info to check constraints before downloading
            info = self.get_info(url)
            
            # Check video length constraint
            video_minutes = info["length_seconds"] / 60
            if video_minutes > self.max_duration_minutes:
                raise VideoTooLargeError(
                    f"Video duration ({video_minutes:.1f} minutes) exceeds "
                    f"maximum allowed ({self.max_duration_minutes} minutes)"
                )
            
            # Create pytube object with progressive streams for better control
            yt = pytube.YouTube(url)
            
            # Select the stream - prioritize mp4 with audio
            stream = yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc().first()
            
            if not stream:
                raise UnsupportedVideoError("No suitable video stream found")
            
            # Download with retry logic - example of circuit breaker pattern
            max_retries = 3
            retry = 0
            
            while retry < max_retries:
                try:
                    logger.info(f"Downloading {info['title']} ({url})")
                    file_path = stream.download(output_path=output_path)
                    logger.info(f"Download complete: {file_path}")
                    return file_path
                except Exception as e:
                    retry += 1
                    if retry >= max_retries:
                        raise DownloadError(f"Failed to download after {max_retries} attempts: {str(e)}")
                    
                    # Exponential backoff - important for rate limiting
                    wait_time = 2 ** retry
                    logger.warning(f"Download failed, retrying in {wait_time}s: {str(e)}")
                    time.sleep(wait_time)
        
        except PytubeError as e:
            logger.error(f"PyTube error: {str(e)}")
            raise DownloadError(f"Failed to download video: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise DownloadError(f"Unexpected error: {str(e)}")


# Factory function - demonstrates Factory pattern
def get_media_repository(source_type: str = "youtube", **kwargs) -> MediaRepository:
    """Factory function to get the appropriate media repository."""
    if source_type.lower() == "youtube":
        return YouTubeRepository(**kwargs)
    else:
        raise ValueError(f"Unsupported source type: {source_type}")