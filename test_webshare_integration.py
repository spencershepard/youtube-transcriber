#!/usr/bin/env python3
"""
Test script for Webshare proxy integration
"""

import os
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig

# Load environment variables
load_dotenv()

def test_webshare_proxy():
    """Test Webshare proxy configuration"""
    webshare_username = os.getenv("WEBSHARE_USERNAME")
    webshare_password = os.getenv("WEBSHARE_PASSWORD")
    
    if not webshare_username or not webshare_password:
        print("❌ WEBSHARE_USERNAME and WEBSHARE_PASSWORD must be set in .env file")
        return False
    
    try:
        # Configure Webshare proxy
        proxy_config = WebshareProxyConfig(
            proxy_username=webshare_username,
            proxy_password=webshare_password
        )
        
        # Create API instance with proxy
        api = YouTubeTranscriptApi(proxy_config=proxy_config)
        
        # Test with a well-known video
        test_video_id = "dQw4w9WgXcQ"  # Rick Roll video
        print(f"🔄 Testing transcript fetch for video: {test_video_id}")
        
        transcript = api.fetch(test_video_id)
        
        if transcript:
            print("✅ Webshare proxy test successful!")
            print(f"📝 Fetched {len(transcript)} transcript segments")
            print(f"🎬 First segment: {transcript[0]['text'][:50]}...")
            return True
        else:
            print("❌ No transcript returned")
            return False
            
    except Exception as e:
        print(f"❌ Webshare proxy test failed: {e}")
        return False

def test_direct_connection():
    """Test direct connection as fallback"""
    try:
        api = YouTubeTranscriptApi()
        test_video_id = "dQw4w9WgXcQ"
        
        print(f"🔄 Testing direct connection for video: {test_video_id}")
        transcript = api.fetch(test_video_id)
        
        if transcript:
            print("✅ Direct connection test successful!")
            print(f"📝 Fetched {len(transcript)} transcript segments")
            return True
        else:
            print("❌ No transcript returned via direct connection")
            return False
            
    except Exception as e:
        print(f"❌ Direct connection test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing YouTube Transcriber Proxy Integration\n")
    
    # Test Webshare proxy
    webshare_success = test_webshare_proxy()
    print()
    
    # Test direct connection fallback
    direct_success = test_direct_connection()
    print()
    
    if webshare_success:
        print("🎉 Webshare proxy integration is working!")
    elif direct_success:
        print("⚠️  Webshare proxy failed, but direct connection works")
    else:
        print("❌ Both proxy and direct connection failed")