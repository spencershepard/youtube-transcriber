# YouTube Transcription API

A FastAPI-based microservice for extracting transcripts from YouTube videos using the `youtube-transcript-api` library. Supports both segmented (with timestamps) and unsegmented transcript formats, with optional proxy support for working around IP restrictions.

** This project was created with Github Co-pilot Agent in VS Code and Claude Sonnet 4. **

## Features

- 🎥 **YouTube Transcript Extraction**: Get transcripts from any YouTube video
- ⏱️ **Segmented & Unsegmented Formats**: Choose between timestamped segments or full text
- � **Segment Filtering**: Limit, merge, sample, or time-filter segments
- ⏰ **Precise Timing**: Timestamps rounded to hundredths of a second (0.01s precision)
- 🌍 **Multi-language Support**: Request transcripts in specific languages
- 🔄 **Translation Support**: Translate transcripts to different languages
- 🔐 **Optional Authentication**: Bearer token authentication for API access
- 🛡️ **Proxy Support**: Built-in support for BrightData residential proxies
- 📊 **Health Checks**: Built-in health monitoring endpoints
- 🚀 **Production Ready**: Dockerized with multi-stage builds and security best practices
- 📖 **Interactive Documentation**: Auto-generated OpenAPI/Swagger docs

## Quick Start

### Using Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd youtube-transcriber
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start the service**
   ```bash
   docker-compose up -d
   ```

4. **Access the API**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Using Docker

```bash
# Build the image
docker build -t youtube-transcriber .

# Run the container
docker run -p 8000:8000 \
  -e BRIGHTDATA_USERNAME=your_username \
  -e BRIGHTDATA_PASSWORD=your_password \
  youtube-transcriber
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

## API Endpoints

### GET `/health`
Health check endpoint
```bash
curl http://localhost:8000/health
```

### GET `/transcript/segmented/{video_id}`
Get transcript with timestamps for each segment

**Parameters:**
- `video_id` (required): YouTube video ID (not full URL)
- `languages` (optional): Comma-separated language codes (e.g., "en,es,fr")
- `translate_to` (optional): Language code to translate to
- `limit` (optional): Maximum number of segments to return
- `merge_segments` (optional): Merge every N consecutive segments into one
- `max_duration` (optional): Only return segments within the first X seconds
- `sample_rate` (optional): Return every Nth segment (e.g., 2 = every other)

**Examples:**
```bash
# Get first 10 segments only
curl "http://localhost:8000/transcript/segmented/dQw4w9WgXcQ?languages=en&limit=10"

# Merge every 3 segments together
curl "http://localhost:8000/transcript/segmented/dQw4w9WgXcQ?languages=en&merge_segments=3"

# Get only first 60 seconds of video
curl "http://localhost:8000/transcript/segmented/dQw4w9WgXcQ?languages=en&max_duration=60"

# Get every 2nd segment (sample rate)
curl "http://localhost:8000/transcript/segmented/dQw4w9WgXcQ?languages=en&sample_rate=2"

# Combine filters: first 30 seconds, merge every 2 segments, limit to 5 results
curl "http://localhost:8000/transcript/segmented/dQw4w9WgXcQ?languages=en&max_duration=30&merge_segments=2&limit=5"
```

**Response:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "language": "English",
  "language_code": "en",
  "is_generated": false,
  "segments": [
    {
      "text": "We're no strangers to love",
      "start": 0.00,
      "duration": 2.54,
      "end": 2.54
    }
  ]
}
```

### GET `/transcript/unsegmented/{video_id}`
Get full transcript as a single text block

**Parameters:**
- `video_id` (required): YouTube video ID
- `languages` (optional): Comma-separated language codes
- `translate_to` (optional): Language code to translate to
- `separator` (optional): Text separator between segments (default: single space)

**Example:**
```bash
curl "http://localhost:8000/transcript/unsegmented/dQw4w9WgXcQ?separator=%20"
```

**Response:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "language": "English",
  "language_code": "en",
  "is_generated": false,
  "full_text": "We're no strangers to love You know the rules and so do I..."
}
```

### GET `/transcript/available/{video_id}`
List all available transcripts for a video

**Example:**
```bash
curl "http://localhost:8000/transcript/available/dQw4w9WgXcQ"
```

**Response:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "transcripts": [
    {
      "language": "English",
      "language_code": "en",
      "is_generated": false,
      "is_translatable": true,
      "translation_languages": ["es", "fr", "de"]
    }
  ]
}
```

## Segment Filtering Options

The `/transcript/segmented/{video_id}` endpoint supports several filtering options to reduce the number of segments returned:

### Filter Types

1. **`limit`** - Limits the total number of segments returned
   - Takes the first N segments after other filters are applied
   - Example: `limit=10` returns only the first 10 segments

2. **`merge_segments`** - Combines consecutive segments
   - Groups every N segments into a single segment
   - Combines text and adjusts timing accordingly
   - Example: `merge_segments=3` combines every 3 segments into 1

3. **`max_duration`** - Time-based filtering
   - Only includes segments that start within the first X seconds
   - Useful for getting just the beginning of long videos
   - Example: `max_duration=60` gets only the first minute

4. **`sample_rate`** - Takes every Nth segment
   - Reduces density by skipping segments
   - Example: `sample_rate=2` takes every other segment

### Timing Precision

All timestamps (start, duration, end) are automatically rounded to **hundredths of a second** (0.01s precision) for:
- ✅ **Cleaner API responses** - No excessive decimal places
- ✅ **Better readability** - Human-friendly timing values
- ✅ **Consistent precision** - Both original and merged segments use same precision

### Filter Processing Order

Filters are applied in this order for optimal results:
1. Time filtering (`max_duration`)
2. Sampling (`sample_rate`) 
3. Merging (`merge_segments`)
4. Limiting (`limit`)

### Practical Use Cases

- **Quick preview**: `?limit=5` - Get just the first few segments
- **Reduce API response size**: `?sample_rate=2&limit=20` - Every other segment, max 20
- **Summary segments**: `?merge_segments=5&limit=10` - Larger text chunks, fewer segments
- **Opening content only**: `?max_duration=120&limit=10` - First 2 minutes, max 10 segments

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `HOST` | No | `0.0.0.0` | Server host |
| `PORT` | No | `8000` | Server port |
| `ENVIRONMENT` | No | `production` | Environment (development/production) |
| `API_TOKEN` | No | - | Bearer token for API authentication (if set, all endpoints require auth) |
| `BRIGHTDATA_USERNAME` | No | - | BrightData proxy username |
| `BRIGHTDATA_PASSWORD` | No | - | BrightData proxy password |
| `BRIGHTDATA_ENDPOINT` | No | `brd.superproxy.io:22225` | BrightData proxy endpoint |

### Proxy Configuration

The service supports BrightData residential proxies to work around IP restrictions that YouTube may impose on cloud servers.

1. **Sign up for BrightData**: https://brightdata.com/
2. **Purchase a residential proxy plan**
3. **Get your credentials** from the dashboard
4. **Set environment variables**:
   ```env
   BRIGHTDATA_USERNAME=your_username
   BRIGHTDATA_PASSWORD=your_password
   ```

Without proxy configuration, the service will attempt direct connections to YouTube, which may be blocked on cloud platforms.

## Authentication

The API supports optional Bearer token authentication. When the `API_TOKEN` environment variable is set, all API endpoints will require a valid Bearer token in the `Authorization` header.

### Setting up Authentication

1. **Set the API token** in your environment:
   ```env
   API_TOKEN=your_secret_token_here
   ```

2. **Make authenticated requests**:
   ```bash
   curl -H "Authorization: Bearer your_secret_token_here" \
        "http://localhost:8000/transcript/segmented/dQw4w9WgXcQ"
   ```

### Authentication Behavior

- **When `API_TOKEN` is not set**: All endpoints are publicly accessible
- **When `API_TOKEN` is set**: All transcript endpoints require valid Bearer token
- **Health endpoint**: Always accessible without authentication (for monitoring)
- **Documentation endpoints**: Always accessible without authentication

### Error Responses

**Missing token:**
```json
{
  "detail": "Bearer token required"
}
```

**Invalid token:**
```json
{
  "detail": "Invalid bearer token"  
}
```

## Deployment

### GitHub Container Registry

The project includes a GitHub Actions workflow that automatically builds and pushes Docker images to GitHub Container Registry (ghcr.io) on pushes to the main branch.

**Using the pre-built image:**
```bash
docker pull ghcr.io/your-username/youtube-transcriber:latest
docker run -p 8000:8000 ghcr.io/your-username/youtube-transcriber:latest
```

### Manual Deployment

1. **Build and tag the image**
   ```bash
   docker build -t youtube-transcriber:v1.0.0 .
   ```

2. **Run with environment variables**
   ```bash
   docker run -d \
     --name youtube-transcriber \
     -p 8000:8000 \
     -e BRIGHTDATA_USERNAME=your_username \
     -e BRIGHTDATA_PASSWORD=your_password \
     --restart unless-stopped \
     youtube-transcriber:v1.0.0
   ```

### Production Considerations

1. **Reverse Proxy**: Use nginx or similar for SSL termination and load balancing
2. **Rate Limiting**: Implement rate limiting to prevent abuse
3. **Monitoring**: Set up logging and monitoring (Prometheus, Grafana)
4. **Scaling**: Use Docker Swarm or Kubernetes for horizontal scaling
5. **Security**: Keep dependencies updated and use security scanning

## Error Handling

The API provides detailed error responses for various scenarios:

- **403 Forbidden**: Transcripts disabled, IP blocked
- **404 Not Found**: Video unavailable, no transcript found
- **429 Too Many Requests**: Rate limiting triggered
- **400 Bad Request**: Invalid translation request
- **500 Internal Server Error**: Unexpected errors

## Development

### Project Structure
```
youtube-transcriber/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── Dockerfile             # Multi-stage Docker build
├── docker-compose.yml     # Development environment
├── .env.example          # Environment template
├── .github/
│   └── workflows/
│       └── docker-build.yml  # CI/CD pipeline
└── README.md             # This file
```

### Running Tests

```bash
# Install development dependencies
pip install pytest httpx

# Run tests (you'll need to create test files)
pytest
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Troubleshooting

### Common Issues

1. **IP Blocked Errors**
   - Solution: Configure BrightData proxy credentials
   - Alternative: Use a VPN or different network

2. **Video Unavailable**
   - Check if the video ID is correct
   - Ensure the video is public and has captions

3. **No Transcript Found**
   - Try different language codes
   - Check if the video has any captions at all

4. **Docker Build Issues**
   - Ensure Docker is installed and running
   - Check system resources (memory, disk space)

### Getting Help

- Check the [FastAPI documentation](https://fastapi.tiangolo.com/)
- Review [youtube-transcript-api docs](https://github.com/jdepoix/youtube-transcript-api)
- Open an issue in this repository