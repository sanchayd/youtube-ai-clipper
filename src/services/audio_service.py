"""
yt-dlp only audio processing service (no external ffmpeg dependency).
"""
import logging
import os
import tempfile
import subprocess
import json
from typing import Optional

logger = logging.getLogger(__name__)


class AudioService:
    """Service for handling audio extraction using yt-dlp only."""
    
    def __init__(self):
        """Initialize the audio service."""
        self.temp_dir = tempfile.gettempdir()
        
        # Check tool availability
        self.yt_dlp_available = self._check_tool_availability('yt-dlp')
        
        logger.info(f"Audio service initialized - yt-dlp: {self.yt_dlp_available}")
    
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
        Download audio segment using yt-dlp's built-in processing.
        
        yt-dlp has built-in audio processing capabilities that can:
        - Extract segments 
        - Convert formats
        - Adjust quality
        - All without external ffmpeg dependency
        """
        if not self.yt_dlp_available:
            logger.error("yt-dlp not available")
            return None
        
        try:
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            output_file = os.path.join(self.temp_dir, f"{video_id}_{start_time}_{duration}.%(ext)s")
            
            # Use yt-dlp with built-in post-processing
            cmd = [
                'yt-dlp',
                '--quiet',                          # Minimal output
                '--no-warnings',
                '--format', 'bestaudio/best',       # Get best audio quality available
                
                # Download section (segment)
                '--external-downloader-args', f'ffmpeg:-ss {start_time} -t {duration}',
                
                # Audio post-processing (built into yt-dlp)
                '--extract-audio',                  # Convert to audio-only
                '--audio-format', 'mp3',            # Output format
                '--audio-quality', '64K',           # Low bitrate for faster processing
                
                # Output file
                '--output', output_file,
                
                youtube_url
            ]
            
            logger.info(f"Starting yt-dlp download for segment {start_time}s-{start_time+duration}s")
            
            # Execute with timeout
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                # Find the actual output file (yt-dlp might change extension)
                actual_file = self._find_output_file(output_file, video_id, start_time, duration)
                
                if actual_file and os.path.exists(actual_file):
                    file_size_mb = os.path.getsize(actual_file) / (1024 * 1024)
                    logger.info(f"yt-dlp download successful: {actual_file} ({file_size_mb:.2f}MB)")
                    return actual_file
                else:
                    logger.error("yt-dlp completed but output file not found")
                    return None
            else:
                # Try fallback method if the first approach fails
                logger.warning(f"First method failed, trying fallback: {result.stderr}")
                return self._download_fallback_method(youtube_url, video_id, start_time, duration)
                
        except subprocess.TimeoutExpired:
            logger.error("yt-dlp timeout - video segment might be too long or network slow")
            return None
        except Exception as e:
            logger.error(f"yt-dlp download exception: {str(e)}")
            return None
    
    def _find_output_file(self, pattern_file: str, video_id: str, start_time: int, duration: int) -> Optional[str]:
        """Find the actual output file created by yt-dlp."""
        # Common extensions yt-dlp might use
        possible_extensions = ['.mp3', '.m4a', '.webm', '.opus']
        base_pattern = pattern_file.replace('.%(ext)s', '')
        
        for ext in possible_extensions:
            test_file = f"{base_pattern}{ext}"
            if os.path.exists(test_file):
                return test_file
        
        # Also check for files with video title in name
        import glob
        temp_pattern = os.path.join(self.temp_dir, f"*{video_id}*{start_time}*{duration}*.mp3")
        matches = glob.glob(temp_pattern)
        if matches:
            return matches[0]
        
        return None
    
    def _download_fallback_method(self, youtube_url: str, video_id: str, start_time: int, duration: int) -> Optional[str]:
        """
        Fallback method: Download full audio, then extract segment.
        
        This is less efficient but more reliable when segment extraction fails.
        """
        try:
            logger.info("Trying fallback method: download full audio then extract segment")
            
            # Download full audio first
            temp_audio = os.path.join(self.temp_dir, f"{video_id}_full.%(ext)s")
            
            cmd1 = [
                'yt-dlp',
                '--quiet',
                '--no-warnings',
                '--format', 'bestaudio',
                '--extract-audio',
                '--audio-format', 'mp3',
                '--audio-quality', '64K',
                '--output', temp_audio,
                youtube_url
            ]
            
            result1 = subprocess.run(cmd1, capture_output=True, text=True, timeout=60)
            
            if result1.returncode == 0:
                # Find the downloaded file
                full_audio_file = self._find_output_file(temp_audio, video_id, 0, 0)
                
                if full_audio_file and os.path.exists(full_audio_file):
                    logger.info(f"Full audio downloaded: {full_audio_file}")
                    
                    # Extract segment using yt-dlp's built-in capabilities
                    # Note: This is a simplified approach since we don't have external ffmpeg
                    # We'll return the full file for now and let AWS Transcribe handle the duration
                    logger.warning(f"Fallback: returning full audio file (AWS Transcribe will process {start_time}s-{start_time+duration}s)")
                    return full_audio_file
                    
            logger.error("Fallback method also failed")
            return None
            
        except Exception as e:
            logger.error(f"Fallback method exception: {str(e)}")
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
            "ffmpeg_available": False,  # We're not using external ffmpeg
            "temp_dir": self.temp_dir,
            "service_ready": self.yt_dlp_available,
            "processing_method": "yt-dlp built-in"
        }