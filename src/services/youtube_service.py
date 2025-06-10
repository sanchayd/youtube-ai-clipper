"""
YouTube service for extracting video metadata and processing URLs.
"""
import logging
import urllib.parse
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class YouTubeService:
    """Service for handling YouTube video operations."""
    
    def __init__(self):
        """Initialize the YouTube service."""
        pass
    
    def extract_video_id(self, url: str) -> str:
        """
        Extract video ID from various YouTube URL formats.
        
        Args:
            url: YouTube URL
            
        Returns:
            Video ID string
            
        Raises:
            ValueError: If video ID cannot be extracted
        """
        try:
            if "youtube.com/watch" in url:
                parsed_url = urllib.parse.urlparse(url)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                return query_params['v'][0]
            elif "youtu.be/" in url:
                return url.split("youtu.be/")[1].split("?")[0]
            else:
                raise ValueError(f"Unsupported YouTube URL format: {url}")
        except (KeyError, IndexError) as e:
            raise ValueError(f"Could not extract video ID from URL: {url}") from e
    
    def get_video_info(self, video_id: str) -> Dict[str, Any]:
        """
        Get video metadata (simulated for demo purposes).
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Dictionary containing video metadata
        """
        # In production, this would call YouTube Data API
        return {
            "id": video_id,
            "title": self._get_simulated_title(video_id),
            "duration_seconds": 120,
            "channel": "Sample Channel",
            "publish_date": "2023-01-01T00:00:00Z",
            "view_count": 10000,
            "thumbnail_url": f"https://i.ytimg.com/vi/{video_id}/default.jpg",
            "description": "Sample video description",
            "tags": ["sample", "demo", "youtube"]
        }
    
    def _get_simulated_title(self, video_id: str) -> str:
        """Get simulated title based on known video IDs."""
        known_videos = {
            "jNQXAC9IVRw": "Me at the zoo",
            "dQw4w9WgXcQ": "Rick Astley - Never Gonna Give You Up"
        }
        return known_videos.get(video_id, "Sample Video Title")
