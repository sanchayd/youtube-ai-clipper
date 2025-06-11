"""
AWS Lambda handler for video processing requests with real YouTube API integration.
"""
import json
import logging
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.youtube_service import YouTubeService
from services.topic_service import TopicService

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    AWS Lambda handler for processing YouTube video analysis requests.
    
    Args:
        event: Lambda event containing request data
        context: Lambda context object
        
    Returns:
        HTTP response with video analysis results
    """
    logger.info(f"Processing request: {event}")
    
    try:
        # Parse request body
        body = _parse_request_body(event)
        
        # Validate required parameters
        youtube_url = body.get('youtube_url')
        if not youtube_url:
            return _error_response(400, 'Missing required parameter: youtube_url')
        
        topic = body.get('topic', 'bitcoin')  # Default topic
        
        # Initialize services
        youtube_service = YouTubeService()
        topic_service = TopicService()
        
        # Extract video ID and get metadata
        video_id = youtube_service.extract_video_id(youtube_url)
        video_info = youtube_service.get_video_info(video_id)
        
        # Get transcript and find topic mentions
        transcript = topic_service.get_simulated_transcript(video_id)
        mentions = topic_service.find_topic_mentions(transcript, topic)
        clips = topic_service.generate_clip_timestamps(mentions)
        
        # Build response with additional API info
        response_data = {
            'status': 'success',
            'video_info': video_info,
            'topic_analysis': {
                'searched_topic': topic,
                'mentions_found': len(mentions),
                'mentions': mentions,
                'suggested_clips': clips
            },
            'transcript_preview': transcript,
            'api_info': {
                'youtube_api_used': video_info.get('api_source') == 'youtube_data_api_v3',
                'environment': 'production' if os.getenv('YOUTUBE_API_KEY') else 'demo'
            },
            'processing_notes': [
                'Video metadata: ' + ('Real YouTube Data API' if video_info.get('api_source') == 'youtube_data_api_v3' else 'Demo data'),
                'Transcript: Simulated data (Whisper integration coming next)',
                'Topic detection: Real algorithm on simulated transcript'
            ]
        }
        
        return _success_response(response_data)
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return _error_response(400, str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return _error_response(500, 'Internal server error')


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
