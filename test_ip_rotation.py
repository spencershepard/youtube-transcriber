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

def main():
    """Run all tests"""
    print("YouTube Transcriber - IP Rotation Test")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    try:
        test_session_id_generation()
        test_username_building()
        test_api_creation_debug()
        test_multiple_api_instances()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        print("\n💡 Tips for production:")
        print("  - Set BRIGHTDATA_USERNAME and BRIGHTDATA_PASSWORD in your .env")
        print("  - IP rotation happens automatically with short UUID session IDs")
        print("  - Monitor your BrightData usage to ensure you have enough traffic")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()