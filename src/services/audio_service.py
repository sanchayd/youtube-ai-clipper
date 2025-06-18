"""
Enhanced audio processing service using yt-dlp for maximum reliability.
"""
import logging
import os
import tempfile
import subprocess
import json
from typing import Optional

logger = logging.getLogger(__name__)


class AudioService:
    """Service for handling audio extraction using yt-dlp + ffmpeg."""
    
    def __init__(self):
        """Initialize the audio service."""
        self.temp_dir = tempfile.gettempdir()
        
        # Check tool availability
        self.yt_dlp_available = self._check_tool_availability('yt-dlp')
        self.ffmpeg_available = self._check_tool_availability('ffmpeg')
        
        logger.info(f"Audio service initialized - yt-dlp: {self.yt_dlp_available}, ffmpeg: {self.ffmpeg_available}")
    
    def _check_tool_availability(self, tool_name: str) -> bool:
        """Check if a command line tool is available."""
        try:
            result = subprocess.run([tool_name, '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except Exception:
            return False
    
    def extract_audio_url(self, video_id: str) -> Optional[str]:
        """
        Extract audio stream URL using yt-dlp.
        
        This method is much more reliable than pytube for getting stream URLs.
        """
        if not self.yt_dlp_available:
            logger.error("yt-dlp not available")
            return None
        
        try:
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            
            # Use yt-dlp to get the best audio stream URL
            cmd = [
                'yt-dlp',
                '--quiet',
                '--no-warnings',
                '--format', 'bestaudio/best',  # Prefer audio-only, fallback to best quality
                '--get-url',
                youtube_url
            ]
            
            logger.info(f"Getting audio URL for {video_id}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and result.stdout.strip():
                audio_url = result.stdout.strip()
                logger.info(f"Successfully extracted audio URL for {video_id}")
                return audio_url
            else:
                logger.error(f"yt-dlp failed to get URL: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error(f"yt-dlp timeout for video {video_id}")
            return None
        except Exception as e:
            logger.error(f"Failed to extract audio URL for {video_id}: {str(e)}")
            return None
    
    def download_audio_segment(self, video_id: str, start_time: int = 0, duration: int = 60) -> Optional[str]:
        """
        Download audio segment using yt-dlp + ffmpeg.
        
        This approach is more reliable than pytube + ffmpeg because:
        1. yt-dlp handles YouTube's API changes better
        2. yt-dlp can do the segmentation itself
        3. Better error handling and retry logic
        """
        if not self.yt_dlp_available or not self.ffmpeg_available:
            logger.error(f"Required tools not available - yt-dlp: {self.yt_dlp_available}, ffmpeg: {self.ffmpeg_available}")
            return None
        
        try:
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            output_file = os.path.join(self.temp_dir, f"{video_id}_{start_time}_{duration}.mp3")
            
            # Method 1: Let yt-dlp handle everything (most reliable)
            return self._download_with_ytdlp_direct(youtube_url, output_file, start_time, duration)
            
        except Exception as e:
            logger.error(f"Failed to download audio segment: {str(e)}")
            return None
    
    def _download_with_ytdlp_direct(self, youtube_url: str, output_file: str, start_time: int, duration: int) -> Optional[str]:
        """
        Use yt-dlp with built-in ffmpeg post-processing for segment extraction.
        
        This is the most reliable approach because yt-dlp handles:
        - YouTube stream URL extraction
        - ffmpeg post-processing
        - Error recovery
        - Format conversion
        """
        try:
            # yt-dlp command with segment extraction and audio processing
            cmd = [
                'yt-dlp',
                '--quiet',                    # Minimal output
                '--no-warnings',
                '--format', 'bestaudio',      # Get best audio quality
                '--extract-audio',            # Convert to audio-only
                '--audio-format', 'mp3',      # Output format
                '--audio-quality', '64K',     # Low bitrate for faster processing
                
                # Segment extraction using ffmpeg post-processor
                '--postprocessor-args', f'ffmpeg:-ss {start_time} -t {duration} -ar 16000 -ac 1',
                
                # Output file (yt-dlp will add extension automatically)
                '--output', output_file.replace('.mp3', '.%(ext)s'),
                
                youtube_url
            ]
            
            logger.info(f"Starting yt-dlp download for segment {start_time}s-{start_time+duration}s")
            
            # Execute with timeout
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
            
            if result.returncode == 0:
                # yt-dlp might have changed the extension, check for the file
                if os.path.exists(output_file):
                    file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
                    logger.info(f"yt-dlp download successful: {output_file} ({file_size_mb:.2f}MB)")
                    return output_file
                else:
                    # Check if file exists with different extension
                    base_name = output_file.replace('.mp3', '')
                    for ext in ['.mp3', '.m4a', '.webm']:
                        alt_file = f"{base_name}{ext}"
                        if os.path.exists(alt_file):
                            logger.info(f"Found output file with different extension: {alt_file}")
                            # Rename to expected extension if needed
                            if alt_file != output_file:
                                os.rename(alt_file, output_file)
                            return output_file
                    
                    logger.error("yt-dlp completed but output file not found")
                    return None
            else:
                logger.error(f"yt-dlp failed with return code {result.returncode}: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("yt-dlp timeout - video segment might be too long or network slow")
            return None
        except Exception as e:
            logger.error(f"yt-dlp download exception: {str(e)}")
            return None
    
    def cleanup_temp_files(self, file_path: str):
        """Clean up temporary audio files."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to cleanup file {file_path}: {str(e)}")
    
    def get_video_info(self, video_id: str) -> dict:
        """
        Get video information using yt-dlp.
        
        This can serve as a backup to the YouTube API.
        """
        if not self.yt_dlp_available:
            return {"error": "yt-dlp not available"}
        
        try:
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            
            cmd = [
                'yt-dlp',
                '--quiet',
                '--no-warnings',
                '--dump-json',  # Get metadata as JSON
                youtube_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                video_info = json.loads(result.stdout)
                return {
                    "id": video_info.get("id"),
                    "title": video_info.get("title"),
                    "duration": video_info.get("duration"),
                    "uploader": video_info.get("uploader"),
                    "view_count": video_info.get("view_count"),
                    "source": "yt-dlp"
                }
            else:
                logger.error(f"yt-dlp info extraction failed: {result.stderr}")
                return {"error": "Failed to get video info"}
                
        except Exception as e:
            logger.error(f"Video info extraction error: {str(e)}")
            return {"error": str(e)}
    
    def get_service_status(self) -> dict:
        """Get status of audio service capabilities."""
        return {
            "yt_dlp_available": self.yt_dlp_available,
            "ffmpeg_available": self.ffmpeg_available,
            "temp_dir": self.temp_dir,
            "service_ready": self.yt_dlp_available and self.ffmpeg_available
        }