"""Test script for downloading YouTube videos."""

import os
import logging
import sys
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.media.downloader import get_media_repository
from src.services.media.exceptions import MediaServiceError

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_youtube_download():
    """Test downloading a YouTube video."""
    # Example video URL (short video for testing)
    url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # First YouTube video ever
    
    try:
        # Get repository from factory
        repo = get_media_repository(
            max_duration_minutes=int(os.getenv("MAX_VIDEO_LENGTH_MINUTES", "120"))
        )
        
        # Get video info
        info = repo.get_info(url)
        logger.info(f"Video info: {info}")
        
        # Download video
        file_path = repo.download(url)
        logger.info(f"Downloaded to: {file_path}")
        
        # Verify file exists and has size
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
        logger.info(f"File size: {file_size:.2f} MB")
        
        return True
    except MediaServiceError as e:
        logger.error(f"Media service error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Testing YouTube downloader...")
    success = test_youtube_download()
    logger.info(f"Test {'succeeded' if success else 'failed'}")