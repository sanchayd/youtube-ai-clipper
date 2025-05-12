import json
import os
import sys
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Add the package directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import your YouTube downloader
from src.services.media.downloader import get_media_repository
from src.services.media.exceptions import MediaServiceError

def lambda_handler(event, context):
    """
    AWS Lambda handler function for YouTube video info retrieval.
    """
    logger.info(f"Received event: {event}")
    
    try:
        # Get YouTube URL from the request
        body = {}
        if event.get('body'):
            body = json.loads(event.get('body', '{}'))
        
        youtube_url = body.get('youtube_url')
        
        if not youtube_url:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing youtube_url parameter'})
            }
            
        # Create the YouTube repository
        repo = get_media_repository(max_duration_minutes=10)
        
        # Get video info
        info = repo.get_info(youtube_url)
        
        # Return the video info
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Video info retrieved successfully',
                'video_info': info
            })
        }
        
    except MediaServiceError as e:
        logger.error(f"Media service error: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }