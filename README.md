# YouTube AI Clipper

An AI-powered tool that extracts relevant clips from YouTube videos based on topic mentions.

## Features
- Extract YouTube video metadata using official YouTube Data API
- Serverless architecture with AWS Lambda and API Gateway
- Topic detection to identify relevant segments
- Automatic clip generation for social media sharing

## Architecture
- AWS Lambda: Runs the core processing logic
- API Gateway: Provides HTTP endpoints for the application
- YouTube Data API: Retrieves video metadata
- Python 3.10: Core programming language

For more details, see ARCHITECTURE.md.

## Local Development Setup

### Prerequisites
- AWS CLI configured with appropriate permissions
- Python 3.10+
- AWS SAM CLI
- A YouTube Data API key

### Installation
1. Clone the repository:
   git clone https://github.com/sanchayd/youtube-ai-clipper.git
   cd youtube-ai-clipper

2. Set up a Python virtual environment:
   python -m venv .venv
   source .venv/bin/activate

3. Install development dependencies:
   pip install -r requirements.txt

4. Create a .env file with your YouTube API key:
   YOUTUBE_API_KEY=your_api_key_here

## Deployment
The application is deployed using AWS SAM:
   cd deployment
   sam build
   sam deploy --guided

## Usage
Once deployed, you can use the API to fetch video metadata:
   curl -X POST \
     https://your-api-endpoint.amazonaws.com/Prod/video-info \
     -H 'Content-Type: application/json' \
     -d '{"youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID"}'

Example response:
   {
     "message": "Video info retrieved successfully",
     "video_info": {
       "id": "VIDEO_ID",
       "title": "Video Title",
       "length_seconds": 120,
       "author": "Channel Name",
       "publish_date": "2023-01-01T00:00:00Z",
       "views": 10000,
       "thumbnail_url": "https://i.ytimg.com/vi/VIDEO_ID/default.jpg"
     }
   }

## Roadmap
- [x] YouTube video metadata retrieval
- [ ] Speech-to-text transcription with timestamps
- [ ] Topic detection for identifying segments
- [ ] Video clip extraction
- [ ] Social media sharing integration

## License
This project is licensed under the MIT License.