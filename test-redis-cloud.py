"""
Test Redis Cloud connection
Run this locally to verify your Redis Cloud URL works before adding to Render
"""
import redis
import sys

def test_redis_connection(redis_url: str):
    """Test Redis connection with the provided URL"""
    print("=" * 70)
    print("🔧 Redis Cloud Connection Test")
    print("=" * 70)
    print(f"\n📍 Testing URL: {redis_url[:40]}...")
    
    try:
        # Create Redis client
        print("\n⏳ Creating Redis client...")
        client = redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=10,
            socket_timeout=10,
            socket_keepalive=True,
            retry_on_timeout=True,
        )
        print("✅ Client created")
        
        # Test PING
        print("\n⏳ Testing PING...")
        response = client.ping()
        print(f"✅ PING successful: {response}")
        
        # Test SET
        print("\n⏳ Testing SET operation...")
        client.set("test_key", "Hello from Redis Cloud!", ex=60)
        print("✅ SET successful (expires in 60s)")
        
        # Test GET
        print("\n⏳ Testing GET operation...")
        value = client.get("test_key")
        print(f"✅ GET successful: '{value}'")
        
        # Test INCR
        print("\n⏳ Testing INCR operation...")
        client.set("counter", 0)
        client.incr("counter")
        counter = client.get("counter")
        print(f"✅ INCR successful: counter = {counter}")
        
        # Test DELETE
        print("\n⏳ Testing DELETE operation...")
        client.delete("test_key", "counter")
        print("✅ DELETE successful")
        
        # Get Redis info
        print("\n📊 Redis Server Info:")
        info = client.info("server")
        print(f"   Version: {info.get('redis_version', 'N/A')}")
        print(f"   Mode: {info.get('redis_mode', 'N/A')}")
        print(f"   OS: {info.get('os', 'N/A')}")
        
        # Get memory info
        memory_info = client.info("memory")
        used_memory = memory_info.get('used_memory_human', 'N/A')
        print(f"   Memory Used: {used_memory}")
        
        # Test connection pool
        print("\n⏳ Testing connection pool...")
        for i in range(5):
            client.ping()
        print("✅ Connection pool working (5 pings)")
        
        print("\n" + "=" * 70)
        print("🎉 ALL TESTS PASSED! Redis Cloud is working perfectly!")
        print("=" * 70)
        print("\n✅ Your Redis URL is ready to use with Render!")
        return True
        
    except redis.exceptions.ConnectionError as e:
        print(f"\n❌ CONNECTION ERROR: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check Redis Cloud console - is database 'Active'?")
        print("   2. Verify URL format: redis://default:PASSWORD@HOST:PORT")
        print("   3. Make sure password is correct (case-sensitive)")
        print("   4. Check if your IP is allowed (Redis Cloud should allow all)")
        return False
        
    except redis.exceptions.AuthenticationError as e:
        print(f"\n❌ AUTHENTICATION ERROR: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check password in Redis Cloud console")
        print("   2. Make sure URL includes 'default:' before password")
        print("   3. Password should not have spaces or quotes")
        return False
        
    except redis.exceptions.TimeoutError as e:
        print(f"\n❌ TIMEOUT ERROR: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check your internet connection")
        print("   2. Verify Redis Cloud region is accessible")
        print("   3. Try a different region in Redis Cloud")
        return False
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        print(f"   Error Type: {type(e).__name__}")
        print("\n💡 Check the error message above for details")
        return False


if __name__ == "__main__":
    print("\n")
    
    # Get Redis URL from command line or prompt
    if len(sys.argv) > 1:
        redis_url = sys.argv[1]
    else:
        print("📝 Enter your Redis Cloud URL:")
        print("   Format: redis://default:PASSWORD@HOST:PORT")
        print("\n   Example:")
        print("   redis://default:abc123@redis-12345.c123.us-east-1-1.ec2.cloud.redislabs.com:12345")
        print()
        redis_url = input("   URL: ").strip()
    
    if not redis_url:
        print("\n❌ No Redis URL provided!")
        print("\nUsage:")
        print("   python test-redis-cloud.py <redis_url>")
        print("\nExample:")
        print('   python test-redis-cloud.py "redis://default:abc123@redis-12345.c123.us-east-1-1.ec2.cloud.redislabs.com:12345"')
        sys.exit(1)
    
    # Validate URL format
    if not redis_url.startswith("redis://"):
        print("\n⚠️  Warning: URL should start with 'redis://'")
        print("   Your URL:", redis_url[:50])
    
    # Run test
    success = test_redis_connection(redis_url)
    
    if success:
        print("\n📋 Next Steps:")
        print("   1. Go to Render Dashboard")
        print("   2. Select your Backend Service")
        print("   3. Go to Environment tab")
        print("   4. Add environment variable:")
        print("      Key: REDIS_URL")
        print(f"      Value: {redis_url[:50]}...")
        print("   5. Save and wait for auto-redeploy (2-3 min)")
        print("   6. Check logs for: '✅ Redis connected successfully'")
        print("\n🚀 You're all set!")
    else:
        print("\n❌ Fix the connection issues before adding to Render")
        print("   See troubleshooting tips above")
    
    print("\n")
    sys.exit(0 if success else 1)
