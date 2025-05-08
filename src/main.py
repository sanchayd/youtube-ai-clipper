import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment():
    """Test that the environment is set up correctly."""
    print("Environment test:")
    required_vars = ['OPENAI_API_KEY', 'TWITTER_API_KEY']
    for var in required_vars:
        status = "✓" if os.getenv(var) else "✗"
        print(f"  {var}: {status}")
    
    try:
        import pytube
        import whisper
        import transformers
        import ffmpeg
        import tweepy
        print("All required packages installed successfully!")
    except ImportError as e:
        print(f"Package import error: {e}")

if __name__ == "__main__":
    print("YouTube AI Clipper - Environment Setup")
    test_environment()