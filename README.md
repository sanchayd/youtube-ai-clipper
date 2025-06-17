# YouTube AI Clipper

An AI-powered serverless application that analyzes YouTube videos to identify topic mentions and generate shareable clips. Built with AWS Lambda, API Gateway, YouTube Data API, and AWS Transcribe for real speech-to-text processing.

## 🚀 Features

- **Real YouTube Integration**: Fetches actual video metadata using YouTube Data API v3
- **AWS Transcribe Integration**: Real speech-to-text transcription with intelligent fallbacks
- **Intelligent Topic Detection**: Advanced algorithms to find topic mentions with confidence scoring
- **Smart Clip Generation**: Creates optimized clips with proper context for social media
- **Serverless Architecture**: Fully managed AWS infrastructure with auto-scaling
- **Cost-Optimized**: 60 minutes free transcription per month, auto-cleanup of temporary files

## 🏗️ Architecture

This project demonstrates production-grade serverless architecture:

- **AWS Lambda**: Serverless compute for video processing
- **API Gateway**: RESTful API endpoints with CORS support
- **AWS Transcribe**: Real speech-to-text with timestamp accuracy
- **Amazon S3**: Temporary storage for audio files with lifecycle policies
- **YouTube Data API v3**: Real video metadata retrieval
- **Service-Oriented Design**: Clean separation of concerns with intelligent fallbacks

For detailed architecture information, see [ARCHITECTURE.md](ARCHITECTURE.md).

## 💰 Cost Structure

### AWS Transcribe Pricing
- **Free Tier**: 60 minutes per month for first 12 months (~6 ten-minute videos)
- **After Free Tier**: $0.024 per minute ($1.44 per hour)
- **Storage**: S3 costs minimal due to 1-day auto-cleanup

### YouTube Data API
- **Free**: 10,000 units per day (each video info request = ~3 units)

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
│   ├── handlers/              # Lambda function handlers
│   ├── services/             # Business logic services
│   │   ├── youtube_service.py         # YouTube Data API integration
│   │   ├── transcription_service.py   # Main transcription orchestrator
│   │   ├── aws_transcribe_service.py  # AWS Transcribe integration
│   │   ├── audio_service.py           # Audio extraction utilities
│   │   └── topic_service.py           # Topic detection algorithms
│   └── utils/                # Utility functions
├── deployment/               # AWS SAM configuration
├── scripts/                 # Build and deployment scripts
└── tests/                  # Unit and integration tests
```

**Service Architecture**
The application follows microservices principles within a single Lambda:

YouTubeService: Video metadata retrieval and URL parsing
AudioService: YouTube audio extraction and processing
AWSTranscribeService: AWS Transcribe job management and result parsing
TranscriptionService: Main orchestrator with intelligent fallbacks
TopicService: Advanced topic detection with confidence scoring

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

`video_info.api_source`: Shows "youtube_data_api_v3" for real data
`transcript_info.source`: Shows "aws_transcribe" or "demo_data"
`api_info.transcription_source`: Indicates which transcription service was used
`processing_notes`: Human-readable status and fallback information

## Roadmap
- [x] YouTube video metadata retrieval
- [ ] Speech-to-text transcription with timestamps
- [ ] Topic detection for identifying segments
- [ ] Video clip extraction
- [ ] Social media sharing integration

## License
This project is licensed under the MIT License.