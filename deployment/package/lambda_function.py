import json
import os
import sys
import logging
import tempfile

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Add the package directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import your services
from src.services.media.downloader import get_media_repository
from src.services.transcription.whisper_service import WhisperTranscriptionService
from src.services.clip_generator.ffmpeg_service import ClipGenerator
from src.services.media.exceptions import MediaServiceError

def lambda_handler(event, context):
    """
    AWS Lambda handler function for YouTube video processing.
    """
    logger.info(f"Received event: {event}")
    
    try:
        # Get request parameters
        body = {}
        if event.get('body'):
            try:
                body = json.loads(event.get('body', '{}'))
            except json.JSONDecodeError:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Invalid JSON in request body'})
                }
        
        youtube_url = body.get('youtube_url')
        topic = body.get('topic', 'bitcoin')  # Default to 'bitcoin' if not specified
        
        if not youtube_url:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing youtube_url parameter'})
            }
        
        # For now, we'll just get video info and return it
        # In a future iteration, we'll implement the full processing pipeline
        repo = get_media_repository(max_duration_minutes=10)
        video_info = repo.get_info(youtube_url)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Video info retrieved successfully',
                'video_info': video_info,
                'next_step': 'Implement audio extraction and transcription'
            })
        }
        
    except MediaServiceError as e:
        logger.error(f"Media service error: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'details': str(e)
            })
        }