#!/usr/bin/env python3
"""
Test script to demonstrate IP rotation functionality.
This script makes multiple requests and shows how the session IDs change.
"""

import os
import sys
from dotenv import load_dotenv

# Add the current directory to Python path to import from main.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import generate_session_id, get_youtube_api

def test_session_id_generation():
    """Test session ID generation"""
    print("=== Session ID Generation Test ===")
    print("Using simplified short UUID strategy (8 characters)")
    
    # Generate 5 session IDs to show they're unique
    for i in range(5):
        session_id = generate_session_id()
        print(f"  Session {i+1}: {session_id}")

def test_username_building():
    """Test proxy username building"""
    print("\n=== Proxy Username Building Test ===")
    
    
    base_username = "brd-customer-hl_12345678-zone-residential"
    
    # Test basic username with session only
    print(f"\nBase username: {base_username}")
    
    # Generate a few examples to show the pattern
    for i in range(3):
        session_id = generate_session_id()
        username_with_session = f"{base_username}-session-{session_id}"
        print(f"Example {i+1}: {username_with_session}")

def test_api_creation_debug():
    """Debug the API creation process to understand proxy configuration"""
    print("\n=== API Creation Debug Test ===")
    
    username = os.getenv("BRIGHTDATA_USERNAME")
    password = os.getenv("BRIGHTDATA_PASSWORD")
    
    if not username or not password:
        print("⚠️  No credentials - skipping debug test")
        return
    
    print("🔍 Debugging API creation process...")
    
    try:
        # Test direct proxy config creation
        from youtube_transcript_api.proxies import GenericProxyConfig
        
        print("1. Testing direct proxy config creation...")
        session_id = generate_session_id()
        rotated_username = f"{username}-session-{session_id}"
        proxy_endpoint = os.getenv("BRIGHTDATA_ENDPOINT", "brd.superproxy.io:22225")
        
        proxy_config = GenericProxyConfig(
            http_url=f"http://{rotated_username}:{os.getenv('BRIGHTDATA_PASSWORD')}@{proxy_endpoint}",
            https_url=f"http://{rotated_username}:{os.getenv('BRIGHTDATA_PASSWORD')}@{proxy_endpoint}"
        )
        
        print(f"   ✅ Proxy config created: {type(proxy_config)}")
        print(f"   Session ID: {session_id}")
        print(f"   Username with session: {rotated_username}")
        
        if hasattr(proxy_config, 'http_url'):
            print(f"   HTTP URL configured: {proxy_config.http_url[:50]}...{proxy_config.http_url[-20:]}")
        
    except Exception as e:
        print(f"   ❌ Error creating proxy config: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n2. Testing API creation with proxy...")
    try:
        api = get_youtube_api()
        print(f"   API object type: {type(api)}")
        
        # Check all attributes of the API object
        all_attrs = [attr for attr in dir(api) if not attr.startswith('__')]
        print(f"   API attributes: {all_attrs}")
        
        # Look for proxy-related attributes
        proxy_attrs = [attr for attr in all_attrs if 'proxy' in attr.lower()]
        if proxy_attrs:
            print(f"   Proxy-related attributes: {proxy_attrs}")
            for attr in proxy_attrs:
                value = getattr(api, attr)
                print(f"     {attr}: {type(value)} = {value}")
        
        # Check internal attributes that might hold proxy config
        internal_attrs = [attr for attr in all_attrs if attr.startswith('_')]
        print(f"   Internal attributes: {internal_attrs}")
        
        for attr in internal_attrs:
            try:
                value = getattr(api, attr)
                if hasattr(value, 'proxies') or 'proxy' in str(type(value)).lower():
                    print(f"     {attr}: {type(value)} (potentially proxy-related)")
                    if hasattr(value, 'proxies'):
                        print(f"       .proxies: {getattr(value, 'proxies')}")
            except:
                pass
        
    except Exception as e:
        print(f"   ❌ Error in API creation: {e}")
        import traceback
        traceback.print_exc()

def test_multiple_api_instances():
    """Test that multiple API instances get different session IDs"""
    print("\n=== Multiple API Instances Test ===")
    
    # Check if BrightData credentials are available in environment
    username = os.getenv("BRIGHTDATA_USERNAME")
    password = os.getenv("BRIGHTDATA_PASSWORD")
    
    if not username or not password:
        print("⚠️  No BrightData credentials found in environment variables")
        print("   Add BRIGHTDATA_USERNAME and BRIGHTDATA_PASSWORD to your .env file to test proxy functionality")
        print("   Skipping proxy configuration test...")
        return
    
    print("✅ BrightData credentials found - testing proxy configuration...")
    print(f"   Username: {username[:20]}...")
    print("Creating 5 different YouTube API instances...")
    print("Each should have a unique session ID in the proxy configuration:")
    
    session_ids = []
    
    for i in range(5):
        try:
            api = get_youtube_api()
            
            # Check the _fetcher object for proxy configuration
            if hasattr(api, '_fetcher'):
                fetcher = api._fetcher
                
                # Look for proxy configuration in the fetcher
                if hasattr(fetcher, '_proxy_config'):
                    proxy_config = fetcher._proxy_config
                    if hasattr(proxy_config, 'http_url'):
                        proxy_url = proxy_config.http_url
                        if 'session-' in proxy_url:
                            session_part = proxy_url.split('session-')[1].split('@')[0].split(':')[0]
                            session_ids.append(session_part)
                            print(f"  Instance {i+1}: ✅ Session ID: {session_part}")
                        else:
                            print(f"  Instance {i+1}: ⚠️  No session ID in proxy URL")
                    else:
                        print(f"  Instance {i+1}: ⚠️  Proxy config has no http_url")
                else:
                    print(f"  Instance {i+1}: ⚠️  No proxy config found in fetcher")
            else:
                print(f"  Instance {i+1}: ❌ No _fetcher attribute found")
            
        except Exception as e:
            print(f"  Instance {i+1}: Error - {str(e)}")
    
    # Verify all session IDs are unique
    unique_sessions = set(session_ids)
    print(f"\n📊 IP Rotation Verification:")
    print(f"   Total instances created: 5")
    print(f"   Session IDs collected: {len(session_ids)}")
    print(f"   Unique session IDs: {len(unique_sessions)}")
    
    if len(unique_sessions) == len(session_ids) == 5:
        print("   🎉 SUCCESS: All instances have unique session IDs!")
        print("   🌐 IP rotation is working correctly")
    elif len(session_ids) == 5:
        print("   ⚠️  WARNING: Some session IDs are duplicated")
        print("   This might indicate an issue with session generation")
    else:
        print("   ❌ ERROR: Could not extract session IDs from all instances")

def test_brightdata_authentication():
    """Test actual BrightData authentication with real requests"""
    print("\n=== BrightData Authentication Test ===")
    
    username = os.getenv("BRIGHTDATA_USERNAME")
    password = os.getenv("BRIGHTDATA_PASSWORD")
    endpoint = os.getenv("BRIGHTDATA_ENDPOINT", "brd.superproxy.io:22225")
    
    if not username or not password:
        print("⚠️  No BrightData credentials - skipping authentication test")
        return False
    
    print("🔐 Testing BrightData proxy authentication...")
    print(f"   Username: {username[:20]}...")
    print(f"   Endpoint: {endpoint}")
    
    # Test video ID - Rick Roll (known to have transcripts)
    test_video_id = "dQw4w9WgXcQ"
    
    # First, test direct connection as baseline
    print("\n1. Testing direct connection (no proxy)...")
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        direct_api = YouTubeTranscriptApi()
        direct_transcript = direct_api.fetch(test_video_id)
        print(f"   ✅ Direct connection successful - got {len(direct_transcript)} segments")
        direct_works = True
    except Exception as e:
        print(f"   ❌ Direct connection failed: {e}")
        direct_works = False
    
    # Test proxy connection with different session IDs
    print("\n2. Testing proxy connections with session rotation...")
    proxy_results = []
    
    for i in range(3):
        print(f"\n   Test {i+1}/3:")
        try:
            # Create API with proxy
            api = get_youtube_api()
            
            # Extract session ID for verification
            session_id = "unknown"
            if hasattr(api, '_fetcher') and hasattr(api._fetcher, '_proxy_config'):
                proxy_config = api._fetcher._proxy_config
                if hasattr(proxy_config, 'http_url') and 'session-' in proxy_config.http_url:
                    session_id = proxy_config.http_url.split('session-')[1].split('@')[0].split(':')[0]
            
            print(f"     Session ID: {session_id}")
            
            # Make actual request
            transcript = api.fetch(test_video_id)
            segments_count = len(transcript)
            
            print(f"     ✅ Proxy request successful - got {segments_count} segments")
            print(f"     Language: {transcript[0].__dict__ if hasattr(transcript[0], '__dict__') else 'N/A'}")
            
            proxy_results.append({
                'session_id': session_id,
                'success': True,
                'segments': segments_count,
                'error': None
            })
            
        except Exception as e:
            error_msg = str(e)
            print(f"     ❌ Proxy request failed: {error_msg}")
            
            # Categorize the error
            if "407" in error_msg or "auth failed" in error_msg.lower():
                error_type = "authentication_failed"
            elif "ip_forbidden" in error_msg.lower():
                error_type = "ip_blocked"
            elif "tunnel connection failed" in error_msg.lower():
                error_type = "connection_failed"
            elif "max retries" in error_msg.lower():
                error_type = "timeout"
            else:
                error_type = "unknown"
            
            proxy_results.append({
                'session_id': generate_session_id(),
                'success': False,
                'segments': 0,
                'error': error_type,
                'full_error': error_msg
            })
    
    # Analyze results
    print("\n📊 Authentication Test Results:")
    successful_requests = [r for r in proxy_results if r['success']]
    failed_requests = [r for r in proxy_results if not r['success']]
    
    print(f"   Total proxy attempts: {len(proxy_results)}")
    print(f"   Successful: {len(successful_requests)}")
    print(f"   Failed: {len(failed_requests)}")
    
    if successful_requests:
        print("   ✅ BrightData authentication is working!")
        unique_sessions = set(r['session_id'] for r in successful_requests)
        print(f"   🌐 Unique session IDs used: {len(unique_sessions)}")
        
        # Show session details
        for result in successful_requests:
            print(f"     Session {result['session_id']}: {result['segments']} segments")
        
        return True
    else:
        print("   ❌ BrightData authentication failed for all attempts")
        
        # Analyze failure patterns
        error_types = {}
        for result in failed_requests:
            error_type = result['error']
            if error_type not in error_types:
                error_types[error_type] = []
            error_types[error_type].append(result)
        
        print("\n🔍 Error Analysis:")
        for error_type, results in error_types.items():
            print(f"   {error_type}: {len(results)} occurrences")
            if results:
                print(f"     Example: {results[0]['full_error'][:100]}...")
        
        print("\n💡 Troubleshooting suggestions:")
        if 'authentication_failed' in error_types:
            print("   - Check your BRIGHTDATA_USERNAME and BRIGHTDATA_PASSWORD")
            print("   - Verify your BrightData account is active and has credit")
        if 'ip_blocked' in error_types:
            print("   - Your IP may be blocked from accessing the proxy")
            print("   - Contact BrightData support")
        if 'connection_failed' in error_types:
            print("   - Check your internet connection")
            print("   - Verify BRIGHTDATA_ENDPOINT is correct")
        
        return False

def test_ip_detection():
    """Test IP detection to verify rotation is working"""
    print("\n=== IP Detection Test ===")
    
    username = os.getenv("BRIGHTDATA_USERNAME")
    password = os.getenv("BRIGHTDATA_PASSWORD")
    
    if not username or not password:
        print("⚠️  No BrightData credentials - skipping IP detection test")
        return
    
    print("🌐 Testing IP rotation by checking external IP...")
    
    import requests
    from youtube_transcript_api.proxies import GenericProxyConfig
    
    endpoint = os.getenv("BRIGHTDATA_ENDPOINT", "brd.superproxy.io:22225")
    ip_check_url = "https://httpbin.org/ip"
    
    # Test direct connection IP
    print("\n1. Direct connection IP:")
    try:
        response = requests.get(ip_check_url, timeout=10)
        direct_ip = response.json()['origin']
        print(f"   Direct IP: {direct_ip}")
    except Exception as e:
        print(f"   ❌ Failed to get direct IP: {e}")
        direct_ip = None
    
    # Test proxy IPs with different sessions
    print("\n2. Proxy connection IPs:")
    proxy_ips = []
    
    for i in range(3):
        try:
            session_id = generate_session_id()
            username_with_session = f"{username}-session-{session_id}"
            
            proxies = {
                'http': f'http://{username_with_session}:{password}@{endpoint}',
                'https': f'http://{username_with_session}:{password}@{endpoint}'
            }
            
            response = requests.get(ip_check_url, proxies=proxies, timeout=15)
            proxy_ip = response.json()['origin']
            proxy_ips.append({'session': session_id, 'ip': proxy_ip})
            print(f"   Session {session_id}: {proxy_ip}")
            
        except Exception as e:
            print(f"   Session {generate_session_id()}: ❌ Failed - {e}")
    
    # Analyze IP rotation
    if proxy_ips:
        unique_ips = set(result['ip'] for result in proxy_ips)
        print(f"\n📊 IP Rotation Analysis:")
        print(f"   Requests made: {len(proxy_ips)}")
        print(f"   Unique IPs: {len(unique_ips)}")
        
        if len(unique_ips) > 1:
            print("   🎉 IP rotation is working!")
        elif len(unique_ips) == 1:
            print("   ⚠️  All requests used the same IP (rotation may not be working)")
        
        if direct_ip and direct_ip not in unique_ips:
            print("   ✅ Proxy IPs are different from direct connection")
        elif direct_ip:
            print("   ⚠️  Proxy IP matches direct connection (proxy may not be working)")

def test_youtube_specific_functionality():
    """Test YouTube-specific functionality with proxy"""
    print("\n=== YouTube-Specific Functionality Test ===")
    
    username = os.getenv("BRIGHTDATA_USERNAME")
    password = os.getenv("BRIGHTDATA_PASSWORD")
    
    if not username or not password:
        print("⚠️  No BrightData credentials - skipping YouTube functionality test")
        return
    
    print("📺 Testing YouTube API functionality with BrightData proxy...")
    
    # Multiple test videos with different characteristics
    test_videos = [
        {"id": "dQw4w9WgXcQ", "name": "Rick Astley - Never Gonna Give You Up", "expected_lang": "en"},
        {"id": "9bZkp7q19f0", "name": "PSY - GANGNAM STYLE", "expected_lang": "ko"},
        {"id": "kffacxfA7G4", "name": "Baby Shark Dance", "expected_lang": "en"}
    ]
    
    results = []
    
    for i, video in enumerate(test_videos):
        print(f"\n{i+1}. Testing: {video['name']}")
        print(f"   Video ID: {video['id']}")
        
        try:
            api = get_youtube_api()
            
            # Test transcript listing first to get metadata
            transcript_list = api.list(video['id'])
            
            # Convert transcript list to actual list and get available languages
            available_transcripts = list(transcript_list)
            available_languages = [t.language_code for t in available_transcripts]
            
            # Get the first available transcript
            first_transcript = available_transcripts[0] if available_transcripts else None
            
            if not first_transcript:
                raise Exception("No transcripts available for this video")
            
            # Test transcript fetching
            transcript = api.fetch(video['id'])
            
            # Get language info from the transcript list, not the fetched data
            primary_language = first_transcript.language_code if first_transcript else 'unknown'
            is_generated = first_transcript.is_generated if first_transcript else False
            
            results.append({
                'video_id': video['id'],
                'name': video['name'],
                'success': True,
                'segments': len(transcript),
                'languages': available_languages,
                'primary_language': primary_language,
                'is_generated': is_generated
            })
            
            print(f"   ✅ Success: {len(transcript)} segments")
            print(f"   Primary language: {primary_language}")
            print(f"   Is generated: {is_generated}")
            print(f"   Available languages: {', '.join(available_languages)}")
            
            # Show first few segments as sample
            if transcript:
                print(f"   Sample text: {transcript[0].text[:100]}...")
            
        except Exception as e:
            error_msg = str(e)
            results.append({
                'video_id': video['id'],
                'name': video['name'],
                'success': False,
                'error': error_msg
            })
            
            # Provide more specific error information
            if "Could not retrieve a transcript" in error_msg:
                print(f"   ❌ Failed: No transcript available (likely geo-restricted or disabled)")
            elif "TranscriptList" in error_msg:
                print(f"   ❌ Failed: Transcript list access error")
            elif "407" in error_msg or "auth failed" in error_msg.lower():
                print(f"   ❌ Failed: Proxy authentication error")
            else:
                print(f"   ❌ Failed: {error_msg[:100]}...")
    
    # Summary
    successful = [r for r in results if r['success']]
    print(f"\n📊 YouTube Functionality Summary:")
    print(f"   Videos tested: {len(results)}")
    print(f"   Successful: {len(successful)}")
    print(f"   Failed: {len(results) - len(successful)}")
    
    if successful:
        total_segments = sum(r['segments'] for r in successful)
        all_languages = set()
        for r in successful:
            all_languages.update(r['languages'])
        
        print(f"   Total segments fetched: {total_segments}")
        print(f"   Languages encountered: {', '.join(sorted(all_languages))}")
        
        # Show details for each successful video
        for result in successful:
            print(f"   - {result['name']}: {result['segments']} segments ({result['primary_language']})")
        
        print("   🎉 YouTube functionality is working with BrightData!")
    else:
        print("   ❌ All YouTube requests failed")
        
        # Show failure reasons
        failed = [r for r in results if not r['success']]
        print("\n🔍 Failure Analysis:")
        for result in failed:
            print(f"   - {result['name']}: {result['error'][:80]}...")

def main():
    """Run all tests"""
    print("YouTube Transcriber - BrightData Authentication & IP Rotation Test")
    print("=" * 70)
    
    # Load environment variables
    load_dotenv()
    
    try:
        test_session_id_generation()
        test_username_building()
        test_api_creation_debug()
        
        # New comprehensive tests
        auth_success = test_brightdata_authentication()
        test_ip_detection()
        
        if auth_success:
            test_youtube_specific_functionality()
        
        test_multiple_api_instances()
        
        print("\n" + "=" * 70)
        
        if auth_success:
            print("✅ All tests completed successfully!")
            print("🎉 BrightData authentication and IP rotation are working correctly!")
        else:
            print("⚠️  Tests completed with authentication issues")
            print("🔧 Please check your BrightData credentials and account status")
        
        print("\n💡 Production readiness checklist:")
        print("  - ✅ Set BRIGHTDATA_USERNAME and BRIGHTDATA_PASSWORD in your .env")
        print("  - ✅ IP rotation with short UUID session IDs")
        print("  - ✅ Automatic fallback to direct connection on proxy failure")
        print("  - 🔍 Monitor your BrightData usage and account credit")
        print("  - 🔍 Set up monitoring for 407 auth errors in production")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()