"""YouTube video downloader service using official YouTube API."""

import os
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import time
from dotenv import load_dotenv

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.services.media.exceptions import DownloadError, UnsupportedVideoError, VideoTooLargeError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class MediaRepository(ABC):
    """Abstract interface for media repositories."""
    
    @abstractmethod
    def get_info(self, url: str) -> Dict[str, Any]:
        """Get metadata about the media."""
        pass


class YouTubeRepository(MediaRepository):
    """Repository implementation for YouTube videos using official API."""
    
    def __init__(self, max_duration_minutes: int = 120):
        """Initialize repository with constraints."""
        self.max_duration_minutes = max_duration_minutes
        self._cache = {}  # Simple in-memory cache for video information
        
        # Get API key from environment
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            logger.warning("YouTube API key not found in environment variables")
            raise ValueError("YouTube API key is required. Set YOUTUBE_API_KEY environment variable.")
            
        logger.info("Initializing YouTube API client")
        self.youtube = build('youtube', 'v3', developerKey=api_key)
    
    def _extract_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL."""
        if "youtube.com/watch" in url:
            import urllib.parse as urlparse
            parsed_url = urlparse.urlparse(url)
            return urlparse.parse_qs(parsed_url.query)['v'][0]
        elif "youtu.be/" in url:
            return url.split("youtu.be/")[1].split("?")[0]
        else:
            raise DownloadError(f"Could not extract video ID from URL: {url}")
    
    def get_info(self, url: str) -> Dict[str, Any]:
        """
        Get metadata about the YouTube video using official API.
        """
        cache_key = f"info_{url}"
        
        # Check cache first
        if cache_key in self._cache:
            logger.info(f"Cache hit for {url}")
            return self._cache[cache_key]
        
        try:
            # Extract video ID from URL
            video_id = self._extract_video_id(url)
            logger.info(f"Extracted video ID: {video_id}")
            
            # Get video info from YouTube API
            response = self.youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=video_id
            ).execute()
            
            # Check if video exists
            if not response['items']:
                raise DownloadError(f"Video not found: {url}")
            
            video = response['items'][0]
            
            # Parse duration (in ISO 8601 format)
            duration_str = video['contentDetails']['duration']
            duration_seconds = self._parse_duration(duration_str)
            
            # Check video length constraint
            video_minutes = duration_seconds / 60
            if video_minutes > self.max_duration_minutes:
                raise VideoTooLargeError(
                    f"Video duration ({video_minutes:.1f} minutes) exceeds "
                    f"maximum allowed ({self.max_duration_minutes} minutes)"
                )
            
            # Extract relevant information
            info = {
                "id": video_id,
                "title": video['snippet']['title'],
                "length_seconds": duration_seconds,
                "author": video['snippet']['channelTitle'],
                "publish_date": video['snippet']['publishedAt'],
                "views": int(video['statistics'].get('viewCount', 0)),
                "thumbnail_url": video['snippet']['thumbnails']['default']['url']
            }
            
            # Cache the result
            self._cache[cache_key] = info
            return info
            
        except HttpError as e:
            logger.error(f"YouTube API error: {str(e)}")
            raise DownloadError(f"YouTube API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise DownloadError(f"Unexpected error processing video: {str(e)}")
    
    def _parse_duration(self, duration_str: str) -> int:
        """Parse ISO 8601 duration to seconds."""
        import isodate
        
        try:
            return int(isodate.parse_duration(duration_str).total_seconds())
        except Exception as e:
            logger.error(f"Error parsing duration: {str(e)}")
            # Fallback parsing if isodate fails
            import re
            hours = re.search(r'(\d+)H', duration_str)
            minutes = re.search(r'(\d+)M', duration_str)
            seconds = re.search(r'(\d+)S', duration_str)
            
            hours = int(hours.group(1)) if hours else 0
            minutes = int(minutes.group(1)) if minutes else 0
            seconds = int(seconds.group(1)) if seconds else 0
            
            return hours * 3600 + minutes * 60 + seconds


# Factory function
def get_media_repository(source_type: str = "youtube", **kwargs) -> MediaRepository:
    """Factory function to get the appropriate media repository."""
    if source_type.lower() == "youtube":
        return YouTubeRepository(**kwargs)
    else:
        raise ValueError(f"Unsupported source type: {source_type}")