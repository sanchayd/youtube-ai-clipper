"""
Enhanced transcription service using AWS Transcribe with intelligent fallbacks.
"""
import logging
import os
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Service for transcribing audio with AWS Transcribe and demo fallbacks."""
    
    def __init__(self):
        """Initialize transcription service."""
        self.bucket_name = os.getenv('TRANSCRIPTION_BUCKET')
        
        if self.bucket_name:
            try:
                from services.aws_transcribe_service import AWSTranscribeService
                self.aws_transcribe = AWSTranscribeService(self.bucket_name)
                logger.info("AWS Transcribe service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize AWS Transcribe: {str(e)}")
                self.aws_transcribe = None
        else:
            logger.warning("TRANSCRIPTION_BUCKET not set - using demo mode")
            self.aws_transcribe = None
    
    def transcribe_video_segment(self, video_id: str, start_time: int = 0, duration: int = 60) -> Dict[str, Any]:
        """
        Transcribe a segment of a YouTube video using AWS Transcribe or fallback.
        
        Args:
            video_id: YouTube video ID
            start_time: Start time in seconds
            duration: Duration in seconds
            
        Returns:
            Transcription result with source indication
        """
        # Try AWS Transcribe first
        if self.aws_transcribe:
            try:
                logger.info(f"Attempting AWS Transcribe for video {video_id}")
                return self._transcribe_with_aws(video_id, start_time, duration)
            except Exception as e:
                logger.error(f"AWS Transcribe failed: {str(e)}")
                logger.info("Falling back to demo transcription")
        
        # Fallback to demo transcription
        return self._get_demo_transcription(video_id)
    
    def _transcribe_with_aws(self, video_id: str, start_time: int, duration: int) -> Dict[str, Any]:
        """Transcribe using AWS Transcribe service."""
        from services.audio_service import AudioService
        
        audio_service = AudioService()
        
        try:
            # Step 1: Extract audio segment
            logger.info(f"Extracting audio for video {video_id} ({start_time}s-{start_time+duration}s)")
            audio_file = audio_service.download_audio_segment(video_id, start_time, duration)
            
            if not audio_file:
                raise Exception("Failed to extract audio segment")
            
            # Step 2: Transcribe with AWS
            logger.info("Starting AWS Transcribe job...")
            result = self.aws_transcribe.transcribe_audio_file(audio_file, video_id)
            
            # Step 3: Adjust timestamps for segment offset
            if result.get("segments"):
                for segment in result["segments"]:
                    segment["start"] += start_time
                    segment["end"] += start_time
            
            # Step 4: Cleanup local audio file
            audio_service.cleanup_temp_files(audio_file)
            
            logger.info(f"AWS Transcribe completed successfully. Found {len(result.get('segments', []))} segments")
            return result
            
        except Exception as e:
            logger.error(f"AWS Transcribe process failed: {str(e)}")
            raise
    
    def _get_demo_transcription(self, video_id: str = None) -> Dict[str, Any]:
        """Get enhanced demo transcription when AWS Transcribe is unavailable."""
        logger.info(f"Using demo transcription for video {video_id}")
        
        if video_id == "jNQXAC9IVRw":
            # Specific transcript for the first YouTube video
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
                "language": "en-US",
                "duration": 19.0,
                "source": "demo_data"
            }
        else:
            # Generic demo transcript for other videos
            return {
                "text": "Welcome to this video about technology and innovation. Today we're going to discuss bitcoin and cryptocurrency. This technology is revolutionizing finance. Let's explore how bitcoin mining works and its impact on the future.",
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
                        "text": "Let's explore how bitcoin mining works and its impact on the future."
                    }
                ],
                "language": "en-US", 
                "duration": 20.0,
                "source": "demo_data"
            }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get the current status of transcription services."""
        return {
            "aws_transcribe_available": self.aws_transcribe is not None,
            "bucket_configured": self.bucket_name is not None,
            "bucket_name": self.bucket_name,
            "fallback_mode": self.aws_transcribe is None
        }
