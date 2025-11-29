"""
Test Upstash Redis connection
Run this locally to verify your Upstash Redis URL works
"""
import redis
import sys

def test_redis_connection(redis_url: str):
    """Test Redis connection with the provided URL"""
    print(f"🔍 Testing Redis connection...")
    print(f"📍 URL: {redis_url[:30]}...")
    
    try:
        # Create Redis client with Upstash-compatible settings
        client = redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=30,
            socket_timeout=30,
            socket_keepalive=True,
            ssl_cert_reqs=None,  # Don't verify SSL for Upstash
            retry_on_timeout=True,
        )
        
        # Test connection
        print("\n⏳ Pinging Redis...")
        response = client.ping()
        print(f"✅ PING successful: {response}")
        
        # Test SET operation
        print("\n⏳ Testing SET operation...")
        client.set("test_key", "Hello from Upstash!")
        print("✅ SET successful")
        
        # Test GET operation
        print("\n⏳ Testing GET operation...")
        value = client.get("test_key")
        print(f"✅ GET successful: {value}")
        
        # Test DELETE operation
        print("\n⏳ Testing DELETE operation...")
        client.delete("test_key")
        print("✅ DELETE successful")
        
        # Get Redis info
        print("\n📊 Redis Info:")
        info = client.info("server")
        print(f"   Redis Version: {info.get('redis_version', 'N/A')}")
        print(f"   OS: {info.get('os', 'N/A')}")
        
        print("\n🎉 All tests passed! Redis is working perfectly!")
        return True
        
    except redis.exceptions.ConnectionError as e:
        print(f"\n❌ Connection Error: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check that your Redis URL is correct")
        print("   2. Verify the URL includes: redis://default:PASSWORD@host:port")
        print("   3. Make sure Upstash database is active")
        return False
        
    except redis.exceptions.TimeoutError as e:
        print(f"\n❌ Timeout Error: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check your internet connection")
        print("   2. Verify Upstash region is accessible")
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        print(f"   Error Type: {type(e).__name__}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🔧 Upstash Redis Connection Test")
    print("=" * 60)
    
    # Get Redis URL from command line or prompt
    if len(sys.argv) > 1:
        redis_url = sys.argv[1]
    else:
        print("\n📝 Enter your Upstash Redis URL:")
        print("   (Format: redis://default:PASSWORD@host:port)")
        redis_url = input("   URL: ").strip()
    
    if not redis_url:
        print("❌ No Redis URL provided!")
        print("\nUsage:")
        print("   python test-upstash-redis.py <redis_url>")
        print("\nExample:")
        print('   python test-upstash-redis.py "redis://default:abc123@us1-example.upstash.io:6379"')
        sys.exit(1)
    
    # Run test
    success = test_redis_connection(redis_url)
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Ready to add this URL to Render!")
        print("\nNext steps:")
        print("1. Go to Render Dashboard")
        print("2. Select your Backend Service")
        print("3. Go to Environment tab")
        print("4. Add: REDIS_URL = <your_upstash_url>")
        print("5. Save and wait for auto-redeploy")
    else:
        print("❌ Fix the connection issues before adding to Render")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
