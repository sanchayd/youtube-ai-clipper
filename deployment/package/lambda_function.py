import json
import os
import sys
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Add the package directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import services
from src.services.media.downloader import get_media_repository
from src.services.media.exceptions import MediaServiceError

def lambda_handler(event, context):
    """
    AWS Lambda handler function for YouTube video info retrieval with simulated topic detection.
    """
    logger.info(f"Received event: {event}")
    
    try:
        # Parse request
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
        topic = body.get('topic', 'bitcoin')
        
        if not youtube_url:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing youtube_url parameter'})
            }
            
        # Get video metadata
        repo = get_media_repository(max_duration_minutes=10)
        info = repo.get_info(youtube_url)
        
        # Simulate topic detection (in a real implementation, this would use Whisper)
        simulated_transcript = [
            "Hi, I'm at the zoo.",
            "This is the first YouTube video ever uploaded.",
            "The elephants here are cool, and I heard someone talking about bitcoin yesterday.",
            "Anyway, that's about it."
        ]
        
        # Find topic mentions
        topic_matches = []
        for i, text in enumerate(simulated_transcript):
            if topic.lower() in text.lower():
                topic_matches.append({
                    "segment": i,
                    "text": text,
                    "start_time": i * 5,  # Simulated timestamp
                    "end_time": (i + 1) * 5  # Simulated timestamp
                })
        
        # Return results
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Video info retrieved successfully',
                'video_info': info,
                'simulated_transcript': simulated_transcript,
                'topic_mentions': topic_matches,
                'note': 'This is using a simulated transcript. Full Whisper integration would be implemented as a separate microservice.'
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
    