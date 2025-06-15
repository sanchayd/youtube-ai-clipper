# YouTube AI Clipper

An AI-powered serverless application that analyzes YouTube videos to identify topic mentions and generate shareable clips. Built with AWS Lambda, API Gateway, and real YouTube Data API integration.

## 🚀 Features

- **Real YouTube Integration**: Fetches actual video metadata using YouTube Data API v3
- **Intelligent Topic Detection**: Advanced algorithms to find topic mentions in video content
- **Smart Clip Generation**: Creates optimized clips with proper context for social media
- **Serverless Architecture**: Scalable AWS Lambda deployment with API Gateway
- **Production-Ready Fallbacks**: Graceful degradation when external APIs are unavailable

## 🏗️ Architecture

This project demonstrates production-grade serverless architecture:

- **AWS Lambda**: Serverless compute for video processing
- **API Gateway**: RESTful API endpoints with CORS support
- **YouTube Data API v3**: Real video metadata retrieval
- **Service-Oriented Design**: Clean separation of concerns
- **Smart Fallbacks**: Intelligent demo data when APIs unavailable

For detailed architecture information, see [ARCHITECTURE.md](ARCHITECTURE.md).

## 🛠️ Local Development

### Prerequisites

- **AWS CLI** configured with appropriate permissions
- **Python 3.10+** 
- **AWS SAM CLI** for serverless deployment
- **YouTube Data API key** (free from Google Cloud Console)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/sanchayd/youtube-ai-clipper.git
   cd youtube-ai-clipper
   ```

2. **Set up a Python virtual environment**:
```
   python -m venv .venv
   source .venv/bin/activate
```

3. **Install development dependencies**:
   `pip install -r src/requirements.txt`

4. **Create a .env file with your YouTube API key**:
   YOUTUBE_API_KEY=your_api_key_here

## Quick Start
1. **Build the application**:
   `./scripts/build.sh`

2. **Deply to AWS**:
   `./scripts/deploy.sh`

3. **Test the API**:
   `  ./scripts/test.sh https://your-api-endpoint.amazonaws.com/Prod` 

## Usage
**Basic Video Analysis**
```
curl -X POST \
  https://your-api-endpoint.amazonaws.com/Prod/analyze \
  -H 'Content-Type: application/json' \
  -d '{
    "youtube_url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
    "topic": "elephant"
  }'
```

** Advanced Parameters**
```
curl -X POST \
  https://your-api-endpoint.amazonaws.com/Prod/analyze \
  -H 'Content-Type: application/json' \
  -d '{
    "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "topic": "bitcoin",
    "duration_limit": 60
  }'
```

** Response Format
```
{
  "status": "success",
  "video_info": {
    "id": "jNQXAC9IVRw",
    "title": "Me at the zoo",
    "duration_seconds": 19,
    "channel": "jawed",
    "view_count": 363825522,
    "api_source": "youtube_data_api_v3"
  },
  "topic_analysis": {
    "searched_topic": "elephant",
    "mentions_found": 1,
    "mentions": [...],
    "suggested_clips": [...]
  },
  "transcript_info": {
    "source": "demo_data",
    "language": "en",
    "summary": {...}
  }
}
```

## 🧪 Development Workflow

** Project Structure**
```
├── src/
│   ├── handlers/          # Lambda function handlers
│   ├── services/          # Business logic services
│   └── utils/            # Utility functions
├── deployment/           # AWS SAM configuration
├── scripts/             # Build and deployment scripts
└── tests/              # Unit and integration tests
```

**Adding New Features**
Create service: Add new service in `src/services/`
Update handler: Modify `src/handlers/video_handler.py`
Test locally: Use SAM CLI for local testing
Deploy: Use deployment scripts

** Best Practices**
Service-oriented design: Each service has a single responsibility
Error handling: Comprehensive error handling with fallbacks
Logging: Structured logging for debugging
Testing: Unit tests for critical business logic

## 🚦 API Status Indicators
The API response includes status indicators showing which services are active:

`api_info.youtube_api_used`: Boolean indicating real YouTube API usage
`transcript_info.source`: Shows transcription source ("demo_data" or "whisper_api")
`processing_notes`: Human-readable status information

## Roadmap
- [x] YouTube video metadata retrieval
- [ ] Speech-to-text transcription with timestamps
- [ ] Topic detection for identifying segments
- [ ] Video clip extraction
- [ ] Social media sharing integration

## License
This project is licensed under the MIT License.