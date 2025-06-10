"""
Topic detection service for analyzing video content.
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class TopicService:
    """Service for detecting topics in video transcripts."""
    
    def __init__(self):
        """Initialize the topic detection service."""
        pass
    
    def get_simulated_transcript(self, video_id: str) -> List[Dict[str, Any]]:
        """
        Get simulated transcript segments.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            List of transcript segments with timestamps
        """
        # Known transcripts for demo
        if video_id == "jNQXAC9IVRw":
            return [
                {
                    "start": 0.0,
                    "end": 5.0,
                    "text": "Alright, so here we are in front of the elephants."
                },
                {
                    "start": 5.0,
                    "end": 10.0,
                    "text": "The cool thing about these guys is that they have really, really, really long trunks."
                },
                {
                    "start": 10.0,
                    "end": 15.0,
                    "text": "And that's cool."
                },
                {
                    "start": 15.0,
                    "end": 20.0,
                    "text": "And that's pretty much all there is to say."
                }
            ]
        else:
            # Generic demo transcript
            return [
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
            ]
    
    def find_topic_mentions(self, transcript: List[Dict[str, Any]], topic: str) -> List[Dict[str, Any]]:
        """
        Find mentions of a specific topic in the transcript.
        
        Args:
            transcript: List of transcript segments
            topic: Topic to search for
            
        Returns:
            List of segments containing the topic
        """
        mentions = []
        topic_lower = topic.lower()
        
        for segment in transcript:
            if topic_lower in segment["text"].lower():
                mentions.append({
                    "segment": segment,
                    "confidence": 0.95,  # Simulated confidence score
                    "context_start": max(0, segment["start"] - 2),  # Add 2s context
                    "context_end": segment["end"] + 2
                })
        
        return mentions
    
    def generate_clip_timestamps(self, mentions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate clip timestamps with context padding.
        
        Args:
            mentions: List of topic mentions
            
        Returns:
            List of clip specifications with start/end times
        """
        clips = []
        
        for i, mention in enumerate(mentions):
            clips.append({
                "clip_id": f"clip_{i+1}",
                "start_time": mention["context_start"],
                "end_time": mention["context_end"],
                "description": f"Clip containing '{mention['segment']['text'][:50]}...'",
                "confidence": mention["confidence"]
            })
        
        return clips
