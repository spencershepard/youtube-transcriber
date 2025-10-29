#!/usr/bin/env python3
"""
Demo script showing how to use the YouTube Transcriber API
with different proxy configurations
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API base URL
BASE_URL = "http://localhost:8000"

def demo_status_check():
    """Check the current API status and proxy configuration"""
    print("🔍 Checking API Status...")
    
    try:
        response = requests.get(f"{BASE_URL}/status")
        response.raise_for_status()
        
        status = response.json()
        print("✅ API Status:")
        print(f"   Proxy Type: {status.get('proxy_type', 'N/A')}")
        print(f"   Proxy Configured: {status.get('proxy_configured', False)}")
        
        if status.get('proxy_details'):
            print(f"   Proxy Details: {json.dumps(status['proxy_details'], indent=6)}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running:")
        print("   python main.py")
        return False
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        return False

def demo_transcript_fetch():
    """Demonstrate transcript fetching"""
    print("\n📝 Fetching Transcript Demo...")
    
    # Test video (Rick Roll - it has reliable transcripts)
    video_id = "dQw4w9WgXcQ"
    
    try:
        # Get segmented transcript
        print(f"Fetching segmented transcript for video: {video_id}")
        response = requests.get(f"{BASE_URL}/transcript/segmented/{video_id}")
        response.raise_for_status()
        
        data = response.json()
        print("✅ Segmented Transcript:")
        print(f"   Video ID: {data['video_id']}")
        print(f"   Language: {data['language']} ({data['language_code']})")
        print(f"   Is Generated: {data['is_generated']}")
        print(f"   Total Segments: {len(data['segments'])}")
        
        # Show first few segments
        print("\n   First 3 segments:")
        for i, segment in enumerate(data['segments'][:3]):
            print(f"     {i+1}. [{segment['start']:.2f}s] {segment['text']}")
        
        # Get unsegmented transcript
        print(f"\nFetching unsegmented transcript for video: {video_id}")
        response = requests.get(f"{BASE_URL}/transcript/unsegmented/{video_id}")
        response.raise_for_status()
        
        data = response.json()
        print("✅ Unsegmented Transcript:")
        print(f"   Full Text Length: {len(data['full_text'])} characters")
        print(f"   Preview: {data['full_text'][:100]}...")
        
        return True
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        if e.response.status_code == 404:
            print("   The video might not have transcripts available")
        return False
    except Exception as e:
        print(f"❌ Error fetching transcript: {e}")
        return False

def demo_health_check():
    """Demonstrate health check"""
    print("\n❤️ Health Check Demo...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        
        health = response.json()
        print("✅ Health Check:")
        print(f"   Status: {health.get('status', 'N/A')}")
        print(f"   Service: {health.get('service', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def main():
    """Run the demo"""
    print("🚀 YouTube Transcriber API Demo")
    print("=" * 50)
    
    # Check if server is running
    if not demo_status_check():
        print("\n💡 To start the server, run:")
        print("   python main.py")
        return
    
    # Run demos
    demo_health_check()
    demo_transcript_fetch()
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed!")
    print("\n💡 Try these endpoints in your browser:")
    print(f"   {BASE_URL}/docs        - Interactive API documentation")
    print(f"   {BASE_URL}/status      - Check proxy configuration")
    print(f"   {BASE_URL}/health      - Health check")

if __name__ == "__main__":
    main()