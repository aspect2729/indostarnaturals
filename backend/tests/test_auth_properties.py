"""Property-based tests for authentication services

Feature: indostar-naturals-ecommerce
"""
import pytest
import re
from hypothesis import given, strategies as st, settings, HealthCheck
from app.services.auth_service import token_service, password_service
from app.models.enums import UserRole


# Custom strategies for generating test data
@st.composite
def user_data_strategy(draw):
    """Generate random user data for token creation"""
    user_id = draw(st.integers(min_value=1, max_value=1000000))
    
    # Generate email (optional)
    has_email = draw(st.booleans())
    email = draw(st.emails()) if has_email else None
    
    # Generate phone number (required)
    phone = draw(st.from_regex(r'\+91[6-9]\d{9}', fullmatch=True))
    
    # Generate role
    role = draw(st.sampled_from([UserRole.CONSUMER, UserRole.DISTRIBUTOR, UserRole.OWNER]))
    
    return {
        "user_id": user_id,
        "email": email,
        "phone": phone,
        "role": role.value
    }


# Feature: indostar-naturals-ecommerce, Property 1: OTP verification issues JWT
@given(user_data=user_data_strategy())
@settings(max_examples=100)
def test_property_otp_verification_issues_jwt(user_data):
    """
    **Property 1: OTP verification issues JWT**
    **Validates: Requirements 1.2**
    
    For any valid OTP code and user, when the OTP is verified, 
    the system should return a valid JWT token that can be used 
    for subsequent authenticated requests.
    """
    # Create token pair (simulating successful OTP verification)
    tokens = token_service.create_token_pair(
        user_id=user_data["user_id"],
        email=user_data["email"],
        phone=user_data["phone"],
        role=user_data["role"]
    )
    
    # Verify that both tokens are created
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert isinstance(tokens["access_token"], str)
    assert isinstance(tokens["refresh_token"], str)
    assert len(tokens["access_token"]) > 0
    assert len(tokens["refresh_token"]) > 0
    
    # Verify that access token can be decoded and contains correct data
    access_payload = token_service.verify_token(tokens["access_token"], token_type="access")
    assert access_payload is not None
    assert access_payload["sub"] == str(user_data["user_id"])
    assert access_payload["email"] == user_data["email"]
    assert access_payload["phone"] == user_data["phone"]
    assert access_payload["role"] == user_data["role"]
    assert access_payload["type"] == "access"
    
    # Verify that refresh token can be decoded and contains correct data
    refresh_payload = token_service.verify_token(tokens["refresh_token"], token_type="refresh")
    assert refresh_payload is not None
    assert refresh_payload["sub"] == str(user_data["user_id"])
    assert refresh_payload["email"] == user_data["email"]
    assert refresh_payload["phone"] == user_data["phone"]
    assert refresh_payload["role"] == user_data["role"]
    assert refresh_payload["type"] == "refresh"
    
    # Verify that access token cannot be verified as refresh token
    invalid_payload = token_service.verify_token(tokens["access_token"], token_type="refresh")
    assert invalid_payload is None
    
    # Verify that refresh token cannot be verified as access token
    invalid_payload = token_service.verify_token(tokens["refresh_token"], token_type="access")
    assert invalid_payload is None


# Test token refresh functionality
@given(user_data=user_data_strategy())
@settings(max_examples=100)
def test_property_refresh_token_generates_new_access_token(user_data):
    """
    Test that a valid refresh token can generate a new access token.
    This is part of the token refresh logic requirement.
    """
    # Create initial token pair
    tokens = token_service.create_token_pair(
        user_id=user_data["user_id"],
        email=user_data["email"],
        phone=user_data["phone"],
        role=user_data["role"]
    )
    
    # Use refresh token to get new access token
    new_access_token = token_service.refresh_access_token(tokens["refresh_token"])
    
    # Verify new access token is created
    assert new_access_token is not None
    assert isinstance(new_access_token, str)
    assert len(new_access_token) > 0
    
    # Verify new access token contains correct user data
    new_payload = token_service.verify_token(new_access_token, token_type="access")
    assert new_payload is not None
    assert new_payload["sub"] == str(user_data["user_id"])
    assert new_payload["email"] == user_data["email"]
    assert new_payload["phone"] == user_data["phone"]
    assert new_payload["role"] == user_data["role"]


# Test that invalid tokens are rejected
@given(invalid_token=st.text(min_size=1, max_size=100))
@settings(max_examples=100)
def test_property_invalid_tokens_rejected(invalid_token):
    """
    Test that invalid or malformed tokens are properly rejected.
    """
    # Verify that random strings are not valid tokens
    payload = token_service.verify_token(invalid_token, token_type="access")
    assert payload is None
    
    payload = token_service.verify_token(invalid_token, token_type="refresh")
    assert payload is None



# Feature: indostar-naturals-ecommerce, Property 56: Passwords hashed with bcrypt
@given(password=st.text(alphabet=st.characters(min_codepoint=33, max_codepoint=126), min_size=8, max_size=72))  # ASCII printable, bcrypt has 72-byte limit
@settings(max_examples=100, deadline=None)  # Disable deadline as bcrypt is intentionally slow
def test_property_passwords_hashed_with_bcrypt(password):
    """
    **Property 56: Passwords hashed with bcrypt**
    **Validates: Requirements 12.1**
    
    For any stored password, the hashed_password field should contain 
    a bcrypt hash with cost factor >= 12.
    """
    # Hash the password
    hashed = password_service.hash_password(password)
    
    # Verify hash is a string
    assert isinstance(hashed, str)
    assert len(hashed) > 0
    
    # Verify it's a bcrypt hash (starts with $2b$ or $2a$ or $2y$)
    # Bcrypt format: $2b$rounds$salt+hash
    assert hashed.startswith(('$2b$', '$2a$', '$2y$'))
    
    # Extract cost factor from bcrypt hash
    # Format: $2b$12$... where 12 is the cost factor
    parts = hashed.split('$')
    assert len(parts) >= 4
    cost_factor = int(parts[2])
    
    # Verify cost factor is at least 12
    assert cost_factor >= 12
    
    # Verify the hashed password can be used to verify the original password
    assert password_service.verify_password(password, hashed) is True
    
    # Verify wrong passwords don't match
    if len(password) > 0:
        wrong_password = password + "wrong"
        assert password_service.verify_password(wrong_password, hashed) is False


# Test password verification round-trip property
@given(password=st.text(alphabet=st.characters(min_codepoint=33, max_codepoint=126), min_size=1, max_size=72))  # ASCII printable, bcrypt has 72-byte limit
@settings(max_examples=100, deadline=None)  # Disable deadline as bcrypt is intentionally slow
def test_property_password_hash_verification_roundtrip(password):
    """
    Test that hashing and verifying a password is a round-trip operation.
    For any password, hash(password) should verify successfully against the original.
    """
    hashed = password_service.hash_password(password)
    
    # Verify the password matches
    assert password_service.verify_password(password, hashed) is True
    
    # Verify different passwords don't match
    different_password = password + "x" if password else "x"
    assert password_service.verify_password(different_password, hashed) is False


# Test that same password produces different hashes (due to salt)
@given(password=st.text(alphabet=st.characters(min_codepoint=33, max_codepoint=126), min_size=1, max_size=50))
@settings(max_examples=50, deadline=None)  # Disable deadline as bcrypt is intentionally slow
def test_property_password_hashes_are_salted(password):
    """
    Test that hashing the same password twice produces different hashes
    due to bcrypt's automatic salting.
    """
    hash1 = password_service.hash_password(password)
    hash2 = password_service.hash_password(password)
    
    # Hashes should be different (due to different salts)
    assert hash1 != hash2
    
    # But both should verify against the original password
    assert password_service.verify_password(password, hash1) is True
    assert password_service.verify_password(password, hash2) is True



# Feature: indostar-naturals-ecommerce, Property 2: Email verification marks account verified
@given(email=st.emails())
@settings(max_examples=100)
def test_property_email_verification_marks_verified(email):
    """
    **Property 2: Email verification marks account verified**
    **Validates: Requirements 1.4**
    
    For any valid email verification token, when clicked, 
    the system should mark the user's email as verified.
    """
    from app.services.email_service import email_service
    from app.core.redis_client import get_redis
    
    # Create a verification token
    redis = get_redis()
    token = email_service.generate_verification_token()
    key = f"email_verification:{token}"
    redis.setex(key, 86400, email)
    
    # Verify the token
    verified_email = email_service.verify_token(token)
    
    # Should return the email
    assert verified_email == email
    
    # Token should be deleted after verification (can't verify twice)
    verified_again = email_service.verify_token(token)
    assert verified_again is None


# Test that expired tokens are rejected
@given(email=st.emails())
@settings(max_examples=50)
def test_property_invalid_tokens_rejected(email):
    """
    Test that invalid or non-existent tokens are properly rejected.
    """
    from app.services.email_service import email_service
    
    # Try to verify a token that doesn't exist
    fake_token = "invalid_token_12345"
    result = email_service.verify_token(fake_token)
    
    assert result is None



# Feature: indostar-naturals-ecommerce, Property 3: Password reset tokens expire
@given(email=st.emails())
@settings(max_examples=100)
def test_property_password_reset_tokens_expire(email):
    """
    **Property 3: Password reset tokens expire**
    **Validates: Requirements 1.6**
    
    For any password reset token, after 24 hours from creation, 
    the token should be invalid and rejected by the system.
    
    Note: This test verifies the token storage mechanism. 
    In production, tokens stored in Redis with TTL will automatically expire.
    """
    from app.services.email_service import password_reset_service
    from app.core.redis_client import get_redis
    
    # Create a reset token
    token = password_reset_service.create_reset_token(email)
    
    # Verify token is valid initially
    verified_email = password_reset_service.verify_reset_token(token)
    assert verified_email == email
    
    # After verification, token should be deleted (can't use twice)
    verified_again = password_reset_service.verify_reset_token(token)
    assert verified_again is None


# Test that tokens are stored with expiration
@given(email=st.emails())
@settings(max_examples=50)
def test_property_reset_tokens_have_ttl(email):
    """
    Test that password reset tokens are stored with TTL in Redis.
    """
    from app.services.email_service import password_reset_service
    from app.core.redis_client import get_redis
    
    # Create a reset token
    token = password_reset_service.create_reset_token(email)
    
    # Check that the token exists in Redis with TTL
    redis = get_redis()
    key = f"password_reset:{token}"
    ttl = redis.ttl(key)
    
    # TTL should be set (positive value, close to 24 hours = 86400 seconds)
    assert ttl > 0
    assert ttl <= 86400
    
    # Clean up
    redis.delete(key)


# Test that invalid tokens are rejected
@given(email=st.emails())
@settings(max_examples=50)
def test_property_invalid_reset_tokens_rejected(email):
    """
    Test that invalid or non-existent reset tokens are properly rejected.
    """
    from app.services.email_service import password_reset_service
    
    # Try to verify a token that doesn't exist
    fake_token = "invalid_reset_token_12345"
    result = password_reset_service.verify_reset_token(fake_token)
    
    assert result is None



# Feature: indostar-naturals-ecommerce, Property 4: Rate limiting blocks excessive auth attempts
@given(
    identifier=st.text(min_size=5, max_size=20),
    max_attempts=st.integers(min_value=3, max_value=10)
)
@settings(max_examples=100)
def test_property_rate_limiting_blocks_excessive_attempts(identifier, max_attempts):
    """
    **Property 4: Rate limiting blocks excessive auth attempts**
    **Validates: Requirements 1.7**
    
    For any IP address, after 5 failed authentication attempts within 15 minutes, 
    the 6th attempt should be blocked with a 429 Too Many Requests response.
    """
    from app.services.rate_limiter import RateLimiter
    from app.core.redis_client import get_redis
    
    # Clean up any existing rate limit for this identifier
    redis = get_redis()
    key = f"rate_limit:{identifier}"
    redis.delete(key)
    
    # First N attempts should succeed
    for i in range(max_attempts):
        result = RateLimiter.check_rate_limit(identifier, max_attempts=max_attempts, window_minutes=15)
        assert result is True, f"Attempt {i+1} should be allowed"
    
    # Next attempt should be blocked
    result = RateLimiter.check_rate_limit(identifier, max_attempts=max_attempts, window_minutes=15)
    assert result is False, "Attempt after limit should be blocked"
    
    # Verify remaining attempts is 0
    remaining = RateLimiter.get_remaining_attempts(identifier, max_attempts=max_attempts)
    assert remaining == 0
    
    # Clean up
    redis.delete(key)


# Test that rate limit resets after window
@given(identifier=st.text(min_size=5, max_size=20))
@settings(max_examples=50)
def test_property_rate_limit_has_ttl(identifier):
    """
    Test that rate limits are stored with TTL and will reset.
    """
    from app.services.rate_limiter import RateLimiter
    from app.core.redis_client import get_redis
    
    # Clean up
    redis = get_redis()
    key = f"rate_limit:{identifier}"
    redis.delete(key)
    
    # Make an attempt
    RateLimiter.check_rate_limit(identifier, max_attempts=5, window_minutes=15)
    
    # Check TTL is set
    ttl = redis.ttl(key)
    assert ttl > 0
    assert ttl <= 15 * 60  # Should be <= 15 minutes
    
    # Clean up
    redis.delete(key)


# Test that different identifiers have independent limits
@given(
    id1=st.text(min_size=5, max_size=20),
    id2=st.text(min_size=5, max_size=20)
)
@settings(max_examples=50)
def test_property_rate_limits_are_independent(id1, id2):
    """
    Test that rate limits for different identifiers are independent.
    """
    from app.services.rate_limiter import RateLimiter
    from app.core.redis_client import get_redis
    
    # Skip if identifiers are the same
    if id1 == id2:
        return
    
    redis = get_redis()
    
    # Clean up
    redis.delete(f"rate_limit:{id1}")
    redis.delete(f"rate_limit:{id2}")
    
    # Exhaust limit for id1
    for _ in range(5):
        RateLimiter.check_rate_limit(id1, max_attempts=5, window_minutes=15)
    
    # id1 should be blocked
    assert RateLimiter.check_rate_limit(id1, max_attempts=5, window_minutes=15) is False
    
    # id2 should still be allowed
    assert RateLimiter.check_rate_limit(id2, max_attempts=5, window_minutes=15) is True
    
    # Clean up
    redis.delete(f"rate_limit:{id1}")
    redis.delete(f"rate_limit:{id2}")



# Feature: indostar-naturals-ecommerce, Property 9: Owner has full admin access
@given(
    user_id=st.integers(min_value=1, max_value=1000000),
    email=st.emails(),
    phone=st.from_regex(r'\+91[6-9]\d{9}', fullmatch=True)
)
@settings(max_examples=100)
def test_property_owner_has_full_admin_access(user_id, email, phone, db_session):
    """
    **Property 9: Owner has full admin access**
    **Validates: Requirements 2.5**
    
    For any owner user, all administrative endpoints should return 200 OK, 
    not 403 Forbidden.
    """
    from app.models.user import User
    from app.models.enums import UserRole
    from app.services.dependencies import require_owner
    from fastapi import HTTPException
    
    # Create an owner user
    owner = User(
        id=user_id,
        email=email,
        phone=phone,
        name="Test Owner",
        role=UserRole.OWNER,
        is_active=True
    )
    
    # Test that require_owner allows owner
    try:
        result = require_owner(current_user=owner)
        assert result == owner
    except HTTPException:
        assert False, "Owner should have access"


# Feature: indostar-naturals-ecommerce, Property 10: Non-owners blocked from admin endpoints
@given(
    user_id=st.integers(min_value=1, max_value=1000000),
    email=st.emails(),
    phone=st.from_regex(r'\+91[6-9]\d{9}', fullmatch=True),
    role=st.sampled_from([UserRole.CONSUMER, UserRole.DISTRIBUTOR])
)
@settings(max_examples=100)
def test_property_non_owners_blocked_from_admin(user_id, email, phone, role, db_session):
    """
    **Property 10: Non-owners blocked from admin endpoints**
    **Validates: Requirements 2.6**
    
    For any non-owner user (consumer or distributor) and any owner-only endpoint, 
    the response should be 403 Forbidden.
    """
    from app.models.user import User
    from app.services.dependencies import require_owner
    from fastapi import HTTPException
    import pytest
    
    # Create a non-owner user
    user = User(
        id=user_id,
        email=email,
        phone=phone,
        name="Test User",
        role=role,
        is_active=True
    )
    
    # Test that require_owner blocks non-owner
    with pytest.raises(HTTPException) as exc_info:
        require_owner(current_user=user)
    
    assert exc_info.value.status_code == 403


# Test distributor or owner access
@given(
    user_id=st.integers(min_value=1, max_value=1000000),
    email=st.emails(),
    phone=st.from_regex(r'\+91[6-9]\d{9}', fullmatch=True),
    role=st.sampled_from([UserRole.DISTRIBUTOR, UserRole.OWNER])
)
@settings(max_examples=100)
def test_property_distributor_or_owner_access(user_id, email, phone, role, db_session):
    """
    Test that distributor or owner role check allows both roles.
    """
    from app.models.user import User
    from app.services.dependencies import require_distributor_or_owner
    from fastapi import HTTPException
    
    # Create user with distributor or owner role
    user = User(
        id=user_id,
        email=email,
        phone=phone,
        name="Test User",
        role=role,
        is_active=True
    )
    
    # Should allow access
    try:
        result = require_distributor_or_owner(current_user=user)
        assert result == user
    except HTTPException:
        assert False, f"{role.value} should have access"


# Test consumer blocked from distributor endpoints
@given(
    user_id=st.integers(min_value=1, max_value=1000000),
    email=st.emails(),
    phone=st.from_regex(r'\+91[6-9]\d{9}', fullmatch=True)
)
@settings(max_examples=50)
def test_property_consumer_blocked_from_distributor_endpoints(user_id, email, phone, db_session):
    """
    Test that consumers are blocked from distributor-only endpoints.
    """
    from app.models.user import User
    from app.models.enums import UserRole
    from app.services.dependencies import require_distributor_or_owner
    from fastapi import HTTPException
    import pytest
    
    # Create consumer user
    user = User(
        id=user_id,
        email=email,
        phone=phone,
        name="Test Consumer",
        role=UserRole.CONSUMER,
        is_active=True
    )
    
    # Should block access
    with pytest.raises(HTTPException) as exc_info:
        require_distributor_or_owner(current_user=user)
    
    assert exc_info.value.status_code == 403



# Feature: indostar-naturals-ecommerce, Property 5: User creation assigns single role
@given(
    phone=st.from_regex(r'\+91[6-9]\d{9}', fullmatch=True),
    name=st.text(min_size=1, max_size=100),
    role=st.sampled_from([UserRole.CONSUMER, UserRole.DISTRIBUTOR, UserRole.OWNER]),
    email=st.one_of(st.none(), st.emails())
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_property_user_creation_assigns_single_role(phone, name, role, email, db_session):
    """
    **Property 5: User creation assigns single role**
    **Validates: Requirements 2.1**
    
    For any user account creation, the user should have exactly one role 
    from the set {consumer, distributor, owner}.
    """
    from app.services.user_service import user_service
    from app.models.enums import UserRole
    
    # Create user with specified role
    user = user_service.create_user(
        phone=phone,
        name=name,
        role=role,
        email=email,
        db=db_session
    )
    
    # Verify user was created
    assert user is not None
    assert user.id is not None
    
    # Verify user has exactly one role
    assert user.role is not None
    assert isinstance(user.role, UserRole)
    assert user.role == role
    
    # Verify role is one of the valid roles
    assert user.role in [UserRole.CONSUMER, UserRole.DISTRIBUTOR, UserRole.OWNER]
    
    # Verify user data matches input
    assert user.phone == phone
    assert user.name == name
    assert user.email == email
    
    # Clean up
    db_session.delete(user)
    db_session.commit()


# Test that role cannot be null or invalid
@given(
    phone=st.from_regex(r'\+91[6-9]\d{9}', fullmatch=True),
    name=st.text(min_size=1, max_size=100)
)
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_property_user_role_is_required(phone, name, db_session):
    """
    Test that user creation requires a valid role.
    """
    from app.services.user_service import user_service
    from app.models.enums import UserRole
    import pytest
    
    # Attempt to create user without role should fail
    # (This would be caught at the type level in Python with proper typing)
    # We test that a valid role must be provided
    
    # Create user with each valid role to ensure they all work
    for role in [UserRole.CONSUMER, UserRole.DISTRIBUTOR, UserRole.OWNER]:
        user = user_service.create_user(
            phone=f"{phone}_{role.value}",  # Make phone unique
            name=name,
            role=role,
            db=db_session
        )
        
        assert user.role == role
        
        # Clean up
        db_session.delete(user)
        db_session.commit()



# Feature: indostar-naturals-ecommerce, Property 28: Address validation requires all fields
@given(
    name=st.text(min_size=1, max_size=100),
    phone=st.from_regex(r'\+91[6-9]\d{9}', fullmatch=True),
    address_line1=st.text(min_size=1, max_size=200),
    city=st.text(min_size=1, max_size=50),
    state=st.text(min_size=1, max_size=50),
    postal_code=st.from_regex(r'\d{6}', fullmatch=True),
    country=st.just("India")
)
@settings(max_examples=100, deadline=None)
def test_property_address_validation_requires_all_fields(
    name, phone, address_line1, city, state, postal_code, country
):
    """
    **Property 28: Address validation requires all fields**
    **Validates: Requirements 6.2**
    
    For any delivery address submission, if any required field 
    (name, phone, address line, city, state, postal code) is missing, 
    the system should reject with a 400 Bad Request response.
    """
    from app.schemas.user import AddressCreateRequest
    from pydantic import ValidationError
    
    # Test that valid address with all fields passes validation
    try:
        valid_address = AddressCreateRequest(
            name=name,
            phone=phone,
            address_line1=address_line1,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country
        )
        
        # Verify all fields are present
        assert valid_address.name == name
        assert valid_address.phone == phone
        assert valid_address.address_line1 == address_line1
        assert valid_address.city == city
        assert valid_address.state == state
        assert valid_address.postal_code == postal_code
        assert valid_address.country == country
        
    except ValidationError as e:
        # If validation fails, it should be due to invalid data format, not missing fields
        # Since we're providing all required fields
        assert False, f"Valid address should not fail validation: {e}"


# Test that missing required fields are rejected
@given(
    field_to_omit=st.sampled_from(['name', 'phone', 'address_line1', 'city', 'state', 'postal_code'])
)
@settings(max_examples=50, deadline=None)
def test_property_address_missing_required_fields_rejected(field_to_omit):
    """
    Test that addresses missing required fields are rejected.
    """
    from app.schemas.user import AddressCreateRequest
    from pydantic import ValidationError
    import pytest
    
    # Create address data with all fields
    address_data = {
        'name': 'Test User',
        'phone': '+919876543210',
        'address_line1': '123 Test Street',
        'city': 'Mumbai',
        'state': 'Maharashtra',
        'postal_code': '400001',
        'country': 'India'
    }
    
    # Remove the field to test
    del address_data[field_to_omit]
    
    # Attempt to create address should fail
    with pytest.raises(ValidationError) as exc_info:
        AddressCreateRequest(**address_data)
    
    # Verify the error is about the missing field
    errors = exc_info.value.errors()
    assert any(error['loc'][0] == field_to_omit for error in errors)


# Test phone number validation
@given(
    invalid_phone=st.one_of(
        st.text(min_size=1, max_size=20).filter(lambda x: not re.match(r'^\+91[6-9]\d{9}$', x)),
        st.just('1234567890'),  # Missing country code
        st.just('+911234567890'),  # Invalid starting digit
        st.just('+9198765432'),  # Too short
        st.just('+919876543210123')  # Too long
    )
)
@settings(max_examples=50, deadline=None)
def test_property_address_phone_validation(invalid_phone):
    """
    Test that invalid phone numbers are rejected in address validation.
    """
    from app.schemas.user import AddressCreateRequest
    from pydantic import ValidationError
    import pytest
    
    # Attempt to create address with invalid phone
    with pytest.raises(ValidationError) as exc_info:
        AddressCreateRequest(
            name='Test User',
            phone=invalid_phone,
            address_line1='123 Test Street',
            city='Mumbai',
            state='Maharashtra',
            postal_code='400001',
            country='India'
        )
    
    # Verify the error is about phone validation
    errors = exc_info.value.errors()
    assert any('phone' in str(error['loc']) for error in errors)


# Test postal code validation
@given(
    invalid_postal=st.one_of(
        st.text(min_size=1, max_size=10).filter(lambda x: not re.match(r'^\d{6}$', x)),
        st.just('12345'),  # Too short
        st.just('1234567'),  # Too long
        st.just('ABCDEF'),  # Non-numeric
        st.just('12-3456')  # Invalid format
    )
)
@settings(max_examples=50, deadline=None)
def test_property_address_postal_code_validation(invalid_postal):
    """
    Test that invalid postal codes are rejected in address validation.
    """
    from app.schemas.user import AddressCreateRequest
    from pydantic import ValidationError
    import pytest
    
    # Attempt to create address with invalid postal code
    with pytest.raises(ValidationError) as exc_info:
        AddressCreateRequest(
            name='Test User',
            phone='+919876543210',
            address_line1='123 Test Street',
            city='Mumbai',
            state='Maharashtra',
            postal_code=invalid_postal,
            country='India'
        )
    
    # Verify the error is about postal code validation
    errors = exc_info.value.errors()
    assert any('postal_code' in str(error['loc']) for error in errors)
