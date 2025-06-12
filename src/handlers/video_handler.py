"""
AWS Lambda handler with real transcription integration.
"""
import json
import logging
import sys
import os

# Configure logging first
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    AWS Lambda handler for processing YouTube video analysis with real transcription.
    """
    logger.info(f"Processing request: {event}")
    
    try:
        # Add src to path for imports
        current_dir = os.path.dirname(__file__)
        parent_dir = os.path.join(current_dir, '..')
        if parent_dir not in sys.path:
            sys.path.append(parent_dir)
        
        # Parse request body
        body = _parse_request_body(event)
        
        # Validate required parameters
        youtube_url = body.get('youtube_url')
        if not youtube_url:
            return _error_response(400, 'Missing required parameter: youtube_url')
        
        topic = body.get('topic', 'bitcoin')
        duration_limit = min(int(body.get('duration_limit', 60)), 120)  # Max 2 minutes for demo
        
        # Import services
        try:
            from services.youtube_service import YouTubeService
            from services.topic_service import TopicService
            from services.transcription_service import TranscriptionService
            logger.info("Successfully imported all services")
        except ImportError as e:
            logger.error(f"Failed to import services: {str(e)}")
            return _error_response(500, f"Service import error: {str(e)}")
        
        # Initialize services
        youtube_service = YouTubeService()
        topic_service = TopicService()
        transcription_service = TranscriptionService()
        
        # Get video metadata
        video_id = youtube_service.extract_video_id(youtube_url)
        video_info = youtube_service.get_video_info(video_id)
        
        # Check if video is too long
        if video_info["duration_seconds"] > duration_limit:
            logger.info(f"Video is {video_info['duration_seconds']}s, processing first {duration_limit}s only")
        
        # Get transcript (real or demo)
        processing_duration = min(video_info["duration_seconds"], duration_limit)
        transcript = transcription_service.transcribe_video_segment(
            video_id, 
            start_time=0, 
            duration=processing_duration
        )
        
        # Analyze transcript for topic mentions
        mentions = topic_service.find_topic_mentions(transcript, topic)
        clips = topic_service.generate_clip_timestamps(mentions)
        transcript_summary = topic_service.get_transcript_summary(transcript)
        
        # Build comprehensive response
        response_data = {
            'status': 'success',
            'video_info': video_info,
            'transcript_info': {
                'source': transcript.get('source', 'unknown'),
                'language': transcript.get('language', 'unknown'),
                'duration_processed': processing_duration,
                'summary': transcript_summary
            },
            'topic_analysis': {
                'searched_topic': topic,
                'mentions_found': len(mentions),
                'mentions': mentions,
                'suggested_clips': clips
            },
            'full_transcript': {
                'segments': transcript.get('segments', []),
                'full_text': transcript.get('text', '')
            },
            'api_info': {
                'youtube_api_used': video_info.get('api_source') == 'youtube_data_api_v3',
                'transcription_source': transcript.get('source', 'unknown'),
                'processing_limited': video_info["duration_seconds"] > duration_limit
            },
            'processing_notes': [
                f'Video metadata: {"Real YouTube Data API" if video_info.get("api_source") == "youtube_data_api_v3" else "Demo data"}',
                f'Transcription: {"Real Whisper API" if transcript.get("source") == "whisper_api" else "Demo/Fallback data"}',
                f'Duration processed: {processing_duration}s of {video_info["duration_seconds"]}s total',
                'Topic detection: Real algorithm on transcript data'
            ]
        }
        
        return _success_response(response_data)
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return _error_response(500, f'Internal server error: {str(e)}')


def _parse_request_body(event):
    """Parse and validate request body."""
    body_str = event.get('body', '{}')
    try:
        return json.loads(body_str)
    except json.JSONDecodeError:
        raise ValueError('Invalid JSON in request body')


def _success_response(data):
    """Create successful response."""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(data, indent=2)
    }


def _error_response(status_code, message):
    """Create error response."""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'status': 'error',
            'message': message
        })
    }
