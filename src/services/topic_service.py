"""
Enhanced topic detection service for analyzing real video transcripts.
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class TopicService:
    """Service for detecting topics in video transcripts."""
    
    def __init__(self):
        """Initialize the topic detection service."""
        pass
    
    def find_topic_mentions(self, transcript: Dict[str, Any], topic: str) -> List[Dict[str, Any]]:
        """
        Find mentions of a specific topic in the transcript.
        
        Args:
            transcript: Transcript dictionary with segments
            topic: Topic to search for
            
        Returns:
            List of segments containing the topic with context
        """
        mentions = []
        topic_lower = topic.lower()
        segments = transcript.get("segments", [])
        
        for i, segment in enumerate(segments):
            if topic_lower in segment["text"].lower():
                # Add context from surrounding segments
                context_segments = self._get_context_segments(segments, i, context_range=1)
                
                mention = {
                    "primary_segment": segment,
                    "context_segments": context_segments,
                    "confidence": self._calculate_confidence(segment["text"], topic),
                    "context_start": context_segments[0]["start"] if context_segments else segment["start"],
                    "context_end": context_segments[-1]["end"] if context_segments else segment["end"],
                    "mention_type": self._classify_mention(segment["text"], topic)
                }
                
                mentions.append(mention)
        
        return mentions
    
    def _get_context_segments(self, segments: List[Dict[str, Any]], target_index: int, context_range: int = 1) -> List[Dict[str, Any]]:
        """Get surrounding segments for context."""
        start_idx = max(0, target_index - context_range)
        end_idx = min(len(segments), target_index + context_range + 1)
        return segments[start_idx:end_idx]
    
    def _calculate_confidence(self, text: str, topic: str) -> float:
        """Calculate confidence score based on context."""
        text_lower = text.lower()
        topic_lower = topic.lower()
        
        # Base confidence if topic is mentioned
        if topic_lower not in text_lower:
            return 0.0
        
        confidence = 0.8  # Base confidence
        
        # Boost confidence for exact matches
        if topic_lower in text_lower.split():
            confidence += 0.1
        
        # Boost for longer contexts
        if len(text.split()) > 10:
            confidence += 0.05
        
        # Boost for financial/tech terms (if searching for bitcoin)
        financial_terms = ["cryptocurrency", "blockchain", "mining", "digital currency", "finance"]
        if topic_lower == "bitcoin" and any(term in text_lower for term in financial_terms):
            confidence += 0.05
        
        return min(confidence, 1.0)
    
    def _classify_mention(self, text: str, topic: str) -> str:
        """Classify the type of mention."""
        text_lower = text.lower()
        
        question_words = ["what", "how", "why", "when", "where"]
        if any(word in text_lower for word in question_words):
            return "question"
        
        if "not" in text_lower or "don't" in text_lower:
            return "negative"
        
        if "like" in text_lower or "love" in text_lower or "great" in text_lower:
            return "positive"
        
        return "neutral"
    
    def generate_clip_timestamps(self, mentions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate optimized clip timestamps with smart context.
        
        Args:
            mentions: List of topic mentions
            
        Returns:
            List of clip specifications with start/end times
        """
        clips = []
        
        for i, mention in enumerate(mentions):
            # Calculate optimal clip duration
            base_duration = mention["context_end"] - mention["context_start"]
            
            # Ensure minimum clip length (5 seconds)
            min_duration = 5.0
            if base_duration < min_duration:
                extension = (min_duration - base_duration) / 2
                start_time = max(0, mention["context_start"] - extension)
                end_time = mention["context_end"] + extension
            else:
                start_time = mention["context_start"]
                end_time = mention["context_end"]
            
            # Ensure maximum clip length (30 seconds for social media)
            max_duration = 30.0
            if end_time - start_time > max_duration:
                end_time = start_time + max_duration
            
            clip = {
                "clip_id": f"clip_{i+1}",
                "start_time": round(start_time, 1),
                "end_time": round(end_time, 1),
                "duration": round(end_time - start_time, 1),
                "primary_text": mention["primary_segment"]["text"],
                "confidence": mention["confidence"],
                "mention_type": mention["mention_type"],
                "description": f"{mention['mention_type'].title()} mention of topic",
                "social_media_ready": end_time - start_time <= 30.0
            }
            
            clips.append(clip)
        
        return clips
    
    def get_transcript_summary(self, transcript: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the transcript."""
        segments = transcript.get("segments", [])
        
        if not segments:
            return {"error": "No segments found"}
        
        total_duration = transcript.get("duration", 0)
        word_count = len(transcript.get("text", "").split())
        
        return {
            "total_segments": len(segments),
            "total_duration": total_duration,
            "word_count": word_count,
            "language": transcript.get("language", "unknown"),
            "words_per_minute": round(word_count / (total_duration / 60), 1) if total_duration > 0 else 0,
            "source": transcript.get("source", "unknown")
        }
