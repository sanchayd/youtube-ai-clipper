import os
import logging
import whisper
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class WhisperTranscriptionService:
    def __init__(self, model_size="base"):
        """Initialize with the specified model size."""
        logger.info(f"Loading Whisper model: {model_size}")
        self.model = whisper.load_model(model_size)
    
    def transcribe_audio(self, audio_file_path: str) -> Dict[str, Any]:
        """
        Transcribe audio file and return transcript with timestamps.
        """
        logger.info(f"Transcribing audio file: {audio_file_path}")
        
        # Transcribe with word-level timestamps
        result = self.model.transcribe(
            audio_file_path, 
            verbose=False,
            word_timestamps=True
        )
        
        return result
    
    def extract_topic_mentions(self, transcription: Dict[str, Any], topic: str) -> List[Dict[str, Any]]:
        """
        Find mentions of a specific topic in the transcript.
        Returns segments where the topic is mentioned.
        """
        topic = topic.lower()
        mentions = []
        
        for segment in transcription["segments"]:
            if topic in segment["text"].lower():
                mentions.append({
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment["text"]
                })
        
        return mentions