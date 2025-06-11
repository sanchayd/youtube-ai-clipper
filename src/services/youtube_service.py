"""
YouTube service for extracting video metadata using YouTube Data API v3.
"""
import logging
import urllib.parse
import os
from typing import Dict, Any, Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import isodate

logger = logging.getLogger(__name__)


class YouTubeService:
    """Service for handling YouTube video operations with real API integration."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the YouTube service.
        
        Args:
            api_key: YouTube Data API key. If None, will try to get from environment.
        """
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY')
        if not self.api_key:
            logger.warning("No YouTube API key provided. Using demo mode.")
            self.youtube = None
        else:
            try:
                self.youtube = build('youtube', 'v3', developerKey=self.api_key)
                logger.info("YouTube API client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize YouTube API client: {str(e)}")
                self.youtube = None
    
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
        Get video metadata using YouTube Data API.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Dictionary containing video metadata
        """
        if not self.youtube:
            logger.warning("YouTube API not available, falling back to demo data")
            return self._get_demo_video_info(video_id)
        
        try:
            # Call YouTube Data API
            response = self.youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=video_id
            ).execute()
            
            if not response['items']:
                raise ValueError(f"Video not found: {video_id}")
            
            video = response['items'][0]
            snippet = video['snippet']
            content_details = video['contentDetails']
            statistics = video['statistics']
            
            # Parse duration from ISO 8601 format
            duration_seconds = self._parse_duration(content_details['duration'])
            
            return {
                "id": video_id,
                "title": snippet['title'],
                "duration_seconds": duration_seconds,
                "channel": snippet['channelTitle'],
                "channel_id": snippet['channelId'],
                "publish_date": snippet['publishedAt'],
                "view_count": int(statistics.get('viewCount', 0)),
                "like_count": int(statistics.get('likeCount', 0)),
                "comment_count": int(statistics.get('commentCount', 0)),
                "thumbnail_url": snippet['thumbnails']['high']['url'],
                "description": snippet['description'][:500] + "..." if len(snippet['description']) > 500 else snippet['description'],
                "tags": snippet.get('tags', []),
                "category_id": snippet['categoryId'],
                "default_language": snippet.get('defaultLanguage', 'unknown'),
                "api_source": "youtube_data_api_v3"
            }
            
        except HttpError as e:
            logger.error(f"YouTube API error: {str(e)}")
            if e.resp.status == 403:
                logger.error("API quota exceeded or invalid API key")
            elif e.resp.status == 404:
                raise ValueError(f"Video not found: {video_id}")
            
            # Fall back to demo data on API error
            logger.warning("Falling back to demo data due to API error")
            return self._get_demo_video_info(video_id)
            
        except Exception as e:
            logger.error(f"Unexpected error calling YouTube API: {str(e)}")
            return self._get_demo_video_info(video_id)
    
    def _parse_duration(self, duration_str: str) -> int:
        """
        Parse ISO 8601 duration string to seconds.
        
        Args:
            duration_str: ISO 8601 duration (e.g., 'PT4M13S')
            
        Returns:
            Duration in seconds
        """
        try:
            duration = isodate.parse_duration(duration_str)
            return int(duration.total_seconds())
        except Exception as e:
            logger.error(f"Error parsing duration '{duration_str}': {str(e)}")
            return 120  # Default fallback
    
    def _get_demo_video_info(self, video_id: str) -> Dict[str, Any]:
        """Get demo video info when API is not available."""
        known_videos = {
            "jNQXAC9IVRw": {
                "title": "Me at the zoo",
                "channel": "jawed",
                "description": "The first video uploaded to YouTube"
            },
            "dQw4w9WgXcQ": {
                "title": "Rick Astley - Never Gonna Give You Up",
                "channel": "RickAstleyVEVO", 
                "description": "The official video for Rick Astley's Never Gonna Give You Up"
            }
        }
        
        video_data = known_videos.get(video_id, {
            "title": "Sample Video Title",
            "channel": "Sample Channel",
            "description": "Sample video description"
        })
        
        return {
            "id": video_id,
            "title": video_data["title"],
            "duration_seconds": 120,
            "channel": video_data["channel"],
            "channel_id": "demo_channel_id",
            "publish_date": "2023-01-01T00:00:00Z",
            "view_count": 10000,
            "like_count": 500,
            "comment_count": 100,
            "thumbnail_url": f"https://i.ytimg.com/vi/{video_id}/default.jpg",
            "description": video_data["description"],
            "tags": ["demo", "sample"],
            "category_id": "22",
            "default_language": "en",
            "api_source": "demo_data"
        }
