"""
Debug handler to identify import and basic functionality issues.
"""
import json
import logging
import sys
import os

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """Debug handler to test basic functionality."""
    logger.info("Debug handler started")
    
    try:
        # Test 1: Basic functionality
        logger.info("Test 1: Basic Python functionality - PASSED")
        
        # Test 2: Environment variables
        api_key = os.getenv('YOUTUBE_API_KEY')
        logger.info(f"Test 2: API key present: {'YES' if api_key else 'NO'}")
        
        # Test 3: Import testing
        try:
            import urllib.parse
            logger.info("Test 3a: urllib.parse import - PASSED")
        except Exception as e:
            logger.error(f"Test 3a: urllib.parse import - FAILED: {str(e)}")
        
        try:
            from googleapiclient.discovery import build
            logger.info("Test 3b: googleapiclient import - PASSED")
        except Exception as e:
            logger.error(f"Test 3b: googleapiclient import - FAILED: {str(e)}")
        
        try:
            import isodate
            logger.info("Test 3c: isodate import - PASSED")
        except Exception as e:
            logger.error(f"Test 3c: isodate import - FAILED: {str(e)}")
        
        # Test 4: Path and imports
        logger.info(f"Python path: {sys.path}")
        logger.info(f"Current directory: {os.getcwd()}")
        logger.info(f"Directory contents: {os.listdir('.')}")
        
        # Test 5: Try importing our services
        try:
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from services.youtube_service import YouTubeService
            logger.info("Test 5a: YouTubeService import - PASSED")
        except Exception as e:
            logger.error(f"Test 5a: YouTubeService import - FAILED: {str(e)}")
        
        try:
            from services.topic_service import TopicService
            logger.info("Test 5b: TopicService import - PASSED")
        except Exception as e:
            logger.error(f"Test 5b: TopicService import - FAILED: {str(e)}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'debug_success',
                'message': 'Debug tests completed. Check CloudWatch logs for details.',
                'api_key_present': bool(api_key)
            })
        }
        
    except Exception as e:
        logger.error(f"Debug handler error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': 'debug_error',
                'error': str(e)
            })
        }
