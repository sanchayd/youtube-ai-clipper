"""
Transcription service using OpenAI's Whisper API.
"""
import logging
import os
from typing import List, Dict, Any, Optional

import openai

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Service for transcribing audio using OpenAI Whisper API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize transcription service.
        
        Args:
            api_key: OpenAI API key. If None, will try to get from environment.
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
            logger.info("OpenAI API key configured")
        else:
            logger.warning("No OpenAI API key found - will use demo transcription")
    
    def transcribe_audio(self, audio_file_path: str) -> Dict[str, Any]:
        """
        Transcribe audio file using Whisper API.
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            Transcription result with timestamps
        """
        if not self.api_key:
            logger.warning("No API key - returning demo transcription")
            return self._get_demo_transcription()
        
        try:
            with open(audio_file_path, 'rb') as audio_file:
                # Use Whisper API for transcription with timestamps
                response = openai.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json",
                    timestamp_granularities=["segment"]
                )
            
            # Convert API response to our format
            segments = []
            for segment in response.segments:
                segments.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip()
                })
            
            return {
                "text": response.text,
                "segments": segments,
                "language": getattr(response, 'language', 'en'),
                "duration": segments[-1]["end"] if segments else 0,
                "source": "whisper_api"
            }
            
        except Exception as e:
            logger.error(f"Whisper API transcription failed: {str(e)}")
            logger.warning("Falling back to demo transcription")
            return self._get_demo_transcription()
    
    def transcribe_video_segment(self, video_id: str, start_time: int = 0, duration: int = 60) -> Dict[str, Any]:
        """
        Transcribe a segment of a YouTube video.
        
        Args:
            video_id: YouTube video ID
            start_time: Start time in seconds
            duration: Duration in seconds
            
        Returns:
            Transcription result
        """
        from services.audio_service import AudioService
        
        audio_service = AudioService()
        
        try:
            # Extract audio segment
            audio_file = audio_service.download_audio_segment(video_id, start_time, duration)
            
            if not audio_file:
                logger.error("Failed to extract audio - using demo transcription")
                return self._get_demo_transcription(video_id)
            
            # Transcribe the audio
            result = self.transcribe_audio(audio_file)
            
            # Adjust timestamps to account for start_time offset
            if result.get("segments"):
                for segment in result["segments"]:
                    segment["start"] += start_time
                    segment["end"] += start_time
            
            # Cleanup temporary file
            audio_service.cleanup_temp_files(audio_file)
            
            return result
            
        except Exception as e:
            logger.error(f"Video transcription failed: {str(e)}")
            return self._get_demo_transcription(video_id)
    
    def _get_demo_transcription(self, video_id: str = None) -> Dict[str, Any]:
        """Get demo transcription when API is not available."""
        if video_id == "jNQXAC9IVRw":
            # Real transcript for the first YouTube video
            return {
                "text": "Alright, so here we are in front of the elephants. The cool thing about these guys is that they have really, really, really long trunks. And that's cool. And that's pretty much all there is to say.",
                "segments": [
                    {
                        "start": 0.0,
                        "end": 5.0,
                        "text": "Alright, so here we are in front of the elephants."
                    },
                    {
                        "start": 5.0,
                        "end": 12.0,
                        "text": "The cool thing about these guys is that they have really, really, really long trunks."
                    },
                    {
                        "start": 12.0,
                        "end": 15.0,
                        "text": "And that's cool."
                    },
                    {
                        "start": 15.0,
                        "end": 19.0,
                        "text": "And that's pretty much all there is to say."
                    }
                ],
                "language": "en",
                "duration": 19.0,
                "source": "demo_data"
            }
        else:
            # Generic demo transcript
            return {
                "text": "Welcome to this video about technology and innovation. Today we're going to discuss bitcoin and cryptocurrency. This technology is revolutionizing finance. Let's explore how bitcoin mining works.",
                "segments": [
                    {
                        "start": 0.0,
                        "end": 5.0,
                        "text": "Welcome to this video about technology and innovation."
                    },
                    {
                        "start": 5.0,
                        "end": 10.0,
                        "text": "Today we're going to discuss bitcoin and cryptocurrency."
                    },
                    {
                        "start": 10.0,
                        "end": 15.0,
                        "text": "This technology is revolutionizing finance."
                    },
                    {
                        "start": 15.0,
                        "end": 20.0,
                        "text": "Let's explore how bitcoin mining works."
                    }
                ],
                "language": "en", 
                "duration": 20.0,
                "source": "demo_data"
            }
