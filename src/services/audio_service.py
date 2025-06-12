"""
Audio processing service for extracting audio from YouTube videos.
"""
import logging
import os
import tempfile
import subprocess
from typing import Optional

logger = logging.getLogger(__name__)


class AudioService:
    """Service for handling audio extraction from YouTube videos."""
    
    def __init__(self):
        """Initialize the audio service."""
        self.temp_dir = tempfile.gettempdir()
    
    def extract_audio_url(self, video_id: str) -> Optional[str]:
        """
        Extract audio stream URL from YouTube video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Audio stream URL or None if extraction fails
        """
        try:
            import pytube
            
            # Create YouTube object
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            yt = pytube.YouTube(youtube_url)
            
            # Get audio stream
            audio_stream = yt.streams.filter(only_audio=True).first()
            
            if not audio_stream:
                logger.error(f"No audio stream found for video {video_id}")
                return None
            
            # Return the URL for the audio stream
            return audio_stream.url
            
        except Exception as e:
            logger.error(f"Failed to extract audio URL for {video_id}: {str(e)}")
            return None
    
    def download_audio_segment(self, video_id: str, start_time: int = 0, duration: int = 60) -> Optional[str]:
        """
        Download a segment of audio from YouTube video.
        
        Args:
            video_id: YouTube video ID
            start_time: Start time in seconds
            duration: Duration in seconds (max 60 for API limits)
            
        Returns:
            Path to downloaded audio file or None if download fails
        """
        try:
            audio_url = self.extract_audio_url(video_id)
            if not audio_url:
                return None
            
            # Create output filename
            output_file = os.path.join(self.temp_dir, f"{video_id}_{start_time}_{duration}.mp3")
            
            # Use ffmpeg to download and extract segment
            ffmpeg_cmd = [
                'ffmpeg',
                '-y',  # Overwrite output file
                '-i', audio_url,
                '-ss', str(start_time),
                '-t', str(duration),
                '-acodec', 'libmp3lame',
                '-ab', '64k',  # Low bitrate to reduce file size
                '-ar', '16000',  # 16kHz sample rate (good for speech)
                output_file
            ]
            
            # Execute ffmpeg command
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg failed: {result.stderr}")
                return None
            
            # Verify file was created and has size
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                logger.info(f"Successfully extracted audio segment: {output_file}")
                return output_file
            else:
                logger.error("Audio file was not created or is empty")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg timeout - video might be too large")
            return None
        except Exception as e:
            logger.error(f"Failed to download audio segment: {str(e)}")
            return None
    
    def cleanup_temp_files(self, file_path: str):
        """Clean up temporary audio files."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to cleanup file {file_path}: {str(e)}")
