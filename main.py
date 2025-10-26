"""
YouTube Transcription API Server

A FastAPI server that provides YouTube video transcription services
using the youtube-transcript-api library with proxy support.
"""

import os
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from dotenv import load_dotenv

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import GenericProxyConfig
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    NotTranslatable,
    TranslationLanguageNotAvailable,
    CookiePathInvalid,
    FailedToCreateConsentCookie,
    RequestBlocked,
    IpBlocked
)

# Load environment variables
load_dotenv()

# Initialize bearer token security
security = HTTPBearer(auto_error=False)

app = FastAPI(
    title="YouTube Transcription API",
    description="Get transcripts from YouTube videos with optional proxy support",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response models
class TranscriptSegment(BaseModel):
    """Individual transcript segment with timing information"""
    text: str = Field(..., description="The transcript text")
    start: float = Field(..., description="Start time in seconds")
    duration: float = Field(..., description="Duration in seconds")
    end: float = Field(..., description="End time in seconds")

class SegmentedTranscriptResponse(BaseModel):
    """Response model for segmented transcript"""
    video_id: str = Field(..., description="YouTube video ID")
    language: str = Field(..., description="Language of the transcript")
    language_code: str = Field(..., description="Language code")
    is_generated: bool = Field(..., description="Whether transcript is auto-generated")
    segments: List[TranscriptSegment] = Field(..., description="List of transcript segments")

class UnsegmentedTranscriptResponse(BaseModel):
    """Response model for unsegmented transcript"""
    video_id: str = Field(..., description="YouTube video ID")
    language: str = Field(..., description="Language of the transcript")
    language_code: str = Field(..., description="Language code")
    is_generated: bool = Field(..., description="Whether transcript is auto-generated")
    full_text: str = Field(..., description="Complete transcript text")

class AvailableTranscript(BaseModel):
    """Model for available transcript information"""
    language: str
    language_code: str
    is_generated: bool
    is_translatable: bool
    translation_languages: List[str]

class AvailableTranscriptsResponse(BaseModel):
    """Response model for available transcripts"""
    video_id: str
    transcripts: List[AvailableTranscript]

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
    video_id: Optional[str] = Field(None, description="Video ID that caused the error")

def verify_bearer_token(credentials: Optional[HTTPAuthorizationCredentials] = Security(security)) -> bool:
    """
    Verify bearer token if API_TOKEN is set in environment variables.
    Returns True if authentication is successful or not required.
    Raises HTTPException if authentication fails.
    """
    api_token = os.getenv("API_TOKEN")
    
    # If no API token is configured, allow access
    if not api_token:
        return True
    
    # If API token is configured but no credentials provided
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Bearer token required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Verify the token
    if credentials.credentials != api_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid bearer token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return True

def get_youtube_api() -> YouTubeTranscriptApi:
    """
    Create and configure YouTubeTranscriptApi instance with proxy if configured
    """
    # Check for BrightData proxy configuration
    proxy_username = os.getenv("BRIGHTDATA_USERNAME")
    proxy_password = os.getenv("BRIGHTDATA_PASSWORD")
    proxy_endpoint = os.getenv("BRIGHTDATA_ENDPOINT", "brd.superproxy.io:22225")
    
    if proxy_username and proxy_password:
        # Configure BrightData residential proxy
        proxy_config = GenericProxyConfig(
            http_url=f"http://{proxy_username}:{proxy_password}@{proxy_endpoint}",
            https_url=f"http://{proxy_username}:{proxy_password}@{proxy_endpoint}"
        )
        return YouTubeTranscriptApi(proxy_config=proxy_config)
    
    # Fallback to direct connection
    return YouTubeTranscriptApi()

def handle_transcript_errors(e: Exception, video_id: str) -> HTTPException:
    """
    Convert youtube-transcript-api exceptions to appropriate HTTP exceptions
    """
    if isinstance(e, TranscriptsDisabled):
        return HTTPException(
            status_code=403,
            detail=f"Transcripts are disabled for video {video_id}"
        )
    elif isinstance(e, NoTranscriptFound):
        return HTTPException(
            status_code=404,
            detail=f"No transcript found for video {video_id} in the requested language(s)"
        )
    elif isinstance(e, VideoUnavailable):
        return HTTPException(
            status_code=404,
            detail=f"Video {video_id} is unavailable"
        )
    elif "429" in str(e) or "too many requests" in str(e).lower():
        return HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later."
        )
    elif isinstance(e, (RequestBlocked, IpBlocked)):
        return HTTPException(
            status_code=403,
            detail="Request blocked. Consider using a proxy service."
        )
    elif isinstance(e, NotTranslatable):
        return HTTPException(
            status_code=400,
            detail="The requested transcript cannot be translated"
        )
    elif isinstance(e, TranslationLanguageNotAvailable):
        return HTTPException(
            status_code=400,
            detail="Translation to the requested language is not available"
        )
    else:
        return HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

def apply_segment_filters(
    segments: List[TranscriptSegment], 
    limit: Optional[int] = None,
    merge_segments: Optional[int] = None,
    max_duration: Optional[float] = None,
    sample_rate: Optional[int] = None
) -> List[TranscriptSegment]:
    """
    Apply various filters to reduce the number of segments returned
    """
    filtered_segments = segments.copy()
    
    # Apply max_duration filter first (affects subsequent filters)
    if max_duration is not None:
        filtered_segments = [s for s in filtered_segments if s.start < max_duration]
    
    # Apply sample_rate filter
    if sample_rate is not None and sample_rate > 1:
        filtered_segments = filtered_segments[::sample_rate]
    
    # Apply merge_segments filter
    if merge_segments is not None and merge_segments > 1:
        merged_segments = []
        for i in range(0, len(filtered_segments), merge_segments):
            batch = filtered_segments[i:i + merge_segments]
            if batch:
                # Merge the batch into a single segment
                merged_text = " ".join([seg.text for seg in batch])
                start_time = batch[0].start
                end_time = batch[-1].end
                merged_segments.append(TranscriptSegment(
                    text=merged_text,
                    start=round(start_time, 2),
                    duration=round(end_time - start_time, 2),
                    end=round(end_time, 2)
                ))
        filtered_segments = merged_segments
    
    # Apply limit filter last
    if limit is not None:
        filtered_segments = filtered_segments[:limit]
    
    return filtered_segments

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "youtube-transcription-api"}

@app.get("/transcript/segmented/{video_id}", response_model=SegmentedTranscriptResponse)
async def get_segmented_transcript(
    video_id: str,
    languages: Optional[str] = Query(None, description="Comma-separated language codes (e.g., 'en,es,fr')"),
    translate_to: Optional[str] = Query(None, description="Language code to translate to"),
    limit: Optional[int] = Query(None, description="Maximum number of segments to return", ge=1),
    merge_segments: Optional[int] = Query(None, description="Merge every N consecutive segments", ge=1),
    max_duration: Optional[float] = Query(None, description="Maximum duration in seconds to include", gt=0),
    sample_rate: Optional[int] = Query(None, description="Return every Nth segment (e.g., 2 = every other)", ge=1),
    authenticated: bool = Depends(verify_bearer_token)
):
    """
    Get a segmented transcript with timing information for each segment
    
    - **video_id**: YouTube video ID (not the full URL)
    - **languages**: Optional comma-separated list of preferred language codes
    - **translate_to**: Optional language code to translate the transcript to
    - **limit**: Maximum number of segments to return (takes first N segments)
    - **merge_segments**: Merge every N consecutive segments into one
    - **max_duration**: Only return segments within the first X seconds of the video
    - **sample_rate**: Return every Nth segment (e.g., 2 = every other segment)
    """
    try:
        api = get_youtube_api()
        
        # Parse languages parameter
        language_list = None
        if languages:
            language_list = [lang.strip() for lang in languages.split(',')]
        
        # Get transcript
        if language_list:
            transcript = api.fetch(video_id, languages=language_list)
        else:
            transcript = api.fetch(video_id)
        
        # Handle translation if requested
        if translate_to:
            transcript_list = api.list(video_id)
            base_transcript = transcript_list.find_transcript(language_list or ['en'])
            translated_transcript = base_transcript.translate(translate_to)
            transcript = translated_transcript.fetch()
        
        # Convert to response format
        segments = []
        for segment in transcript:
            segments.append(TranscriptSegment(
                text=segment.text,
                start=round(segment.start, 2),
                duration=round(segment.duration, 2),
                end=round(segment.start + segment.duration, 2)
            ))
        
        # Apply segment reduction filters
        segments = apply_segment_filters(segments, limit, merge_segments, max_duration, sample_rate)
        
        return SegmentedTranscriptResponse(
            video_id=transcript.video_id,
            language=transcript.language,
            language_code=transcript.language_code,
            is_generated=transcript.is_generated,
            segments=segments
        )
        
    except Exception as e:
        raise handle_transcript_errors(e, video_id)

@app.get("/transcript/unsegmented/{video_id}", response_model=UnsegmentedTranscriptResponse)
async def get_unsegmented_transcript(
    video_id: str,
    languages: Optional[str] = Query(None, description="Comma-separated language codes (e.g., 'en,es,fr')"),
    translate_to: Optional[str] = Query(None, description="Language code to translate to"),
    separator: str = Query(" ", description="Separator between transcript segments"),
    authenticated: bool = Depends(verify_bearer_token)
):
    """
    Get a full unsegmented transcript as a single text block
    
    - **video_id**: YouTube video ID (not the full URL)
    - **languages**: Optional comma-separated list of preferred language codes
    - **translate_to**: Optional language code to translate the transcript to
    - **separator**: Text separator between segments (default: single space)
    """
    try:
        api = get_youtube_api()
        
        # Parse languages parameter
        language_list = None
        if languages:
            language_list = [lang.strip() for lang in languages.split(',')]
        
        # Get transcript
        if language_list:
            transcript = api.fetch(video_id, languages=language_list)
        else:
            transcript = api.fetch(video_id)
        
        # Handle translation if requested
        if translate_to:
            transcript_list = api.list(video_id)
            base_transcript = transcript_list.find_transcript(language_list or ['en'])
            translated_transcript = base_transcript.translate(translate_to)
            transcript = translated_transcript.fetch()
        
        # Combine all segments into single text
        full_text = separator.join([segment.text for segment in transcript])
        
        return UnsegmentedTranscriptResponse(
            video_id=transcript.video_id,
            language=transcript.language,
            language_code=transcript.language_code,
            is_generated=transcript.is_generated,
            full_text=full_text
        )
        
    except Exception as e:
        raise handle_transcript_errors(e, video_id)

@app.get("/transcript/available/{video_id}", response_model=AvailableTranscriptsResponse)
async def get_available_transcripts(
    video_id: str,
    authenticated: bool = Depends(verify_bearer_token)
):
    """
    Get list of available transcripts for a video
    
    - **video_id**: YouTube video ID (not the full URL)
    """
    try:
        api = get_youtube_api()
        transcript_list = api.list(video_id)
        
        transcripts = []
        for transcript in transcript_list:
            transcripts.append(AvailableTranscript(
                language=transcript.language,
                language_code=transcript.language_code,
                is_generated=transcript.is_generated,
                is_translatable=transcript.is_translatable,
                translation_languages=[lang.language_code for lang in transcript.translation_languages]
            ))
        
        return AvailableTranscriptsResponse(
            video_id=video_id,
            transcripts=transcripts
        )
        
    except Exception as e:
        raise handle_transcript_errors(e, video_id)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("ENVIRONMENT") == "development"
    )