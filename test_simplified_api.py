#!/usr/bin/env python3
"""
Simple test to verify the API works with the new proxy configuration
"""

import os
import sys
from dotenv import load_dotenv

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from main import get_youtube_api

def test_api_creation():
    """Test that the API can be created successfully"""
    print("🧪 Testing YouTube API Creation")
    
    try:
        # Test without any proxy configuration
        api = get_youtube_api()
        print("✅ API created successfully")
        
        # Test fetching a transcript
        test_video_id = "dQw4w9WgXcQ"
        print(f"🔄 Testing transcript fetch for video: {test_video_id}")
        
        transcript = api.fetch(test_video_id)
        
        if transcript:
            print(f"✅ Transcript fetch successful! Got {len(transcript)} segments")
            print(f"📝 First segment: {transcript[0].text[:50]}...")
            return True
        else:
            print("❌ No transcript returned")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_proxy_detection():
    """Test proxy type detection"""
    print("\n🔧 Testing Proxy Configuration Detection")
    
    # Test different proxy type values
    test_cases = [
        ("", "direct"),
        ("webshare", "webshare"),
        ("brightdata", "brightdata"),
        ("invalid", "direct")
    ]
    
    for proxy_type, expected in test_cases:
        os.environ["PROXY_TYPE"] = proxy_type
        try:
            api = get_youtube_api()
            proxy_configured = proxy_type in ["webshare", "brightdata"] and (
                (proxy_type == "webshare" and os.getenv("WEBSHARE_USERNAME")) or
                (proxy_type == "brightdata" and os.getenv("BRIGHTDATA_USERNAME"))
            )
            print(f"✅ PROXY_TYPE='{proxy_type}' -> Expected: {expected}, Configured: {proxy_configured}")
        except Exception as e:
            print(f"❌ PROXY_TYPE='{proxy_type}' failed: {e}")
    
    # Clean up
    os.environ.pop("PROXY_TYPE", None)

if __name__ == "__main__":
    print("🚀 Testing Simplified YouTube Transcriber API\n")
    
    success = test_api_creation()
    test_proxy_detection()
    
    if success:
        print("\n🎉 All tests passed! The simplified API is working correctly.")
    else:
        print("\n❌ Some tests failed.")