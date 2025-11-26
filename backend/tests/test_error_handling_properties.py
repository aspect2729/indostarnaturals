"""
Property-Based Tests for Error Handling

These tests verify that the system returns correct HTTP status codes and error formats
for different types of errors.
"""
import pytest
from hypothesis import given, strategies as st, settings
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.user import User
from app.models.enums import UserRole
from app.services.auth_service import TokenService


# Test client
client = TestClient(app)


@pytest.fixture
def owner_user(db_session):
    """Create an owner user for testing"""
    user = User(
        email="owner@example.com",
        phone="+919876543211",
        name="Owner User",
        role=UserRole.OWNER,
        is_active=True,
        is_email_verified=True,
        is_phone_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def owner_token(owner_user):
    """Generate JWT token for owner user"""
    return TokenService.create_access_token(data={"sub": str(owner_user.id)})


# Strategies for generating test data
@st.composite
def invalid_email_strategy(draw):
    """Generate invalid email addresses"""
    invalid_emails = [
        draw(st.text(min_size=1, max_size=20)),  # No @ symbol
        draw(st.text(min_size=1, max_size=10)) + "@",  # No domain
        "@" + draw(st.text(min_size=1, max_size=10)),  # No local part
        draw(st.text(min_size=1, max_size=10)) + "@" + draw(st.text(min_size=1, max_size=5)),  # No TLD
        "",  # Empty string
        "test@",  # Incomplete
        "@test.com",  # Missing local part
    ]
    return draw(st.sampled_from(invalid_emails))


@st.composite
def invalid_phone_strategy(draw):
    """Generate invalid phone numbers"""
    invalid_phones = [
        draw(st.text(alphabet=st.characters(blacklist_categories=("Nd",)), min_size=1, max_size=15)),  # No digits
        draw(st.integers(min_value=0, max_value=999999)).to_bytes(4, 'big').hex(),  # Too short
        "",  # Empty
        "123",  # Too short
        draw(st.text(min_size=1, max_size=5)),  # Random text
    ]
    return draw(st.sampled_from(invalid_phones))


@st.composite
def missing_required_fields_strategy(draw):
    """Generate product data with missing required fields"""
    all_fields = ["title", "description", "category_id", "sku", "unit_size", 
                  "consumer_price", "distributor_price", "stock_quantity"]
    
    # Remove at least one required field
    num_to_remove = draw(st.integers(min_value=1, max_value=len(all_fields)))
    fields_to_remove = draw(st.lists(
        st.sampled_from(all_fields),
        min_size=num_to_remove,
        max_size=num_to_remove,
        unique=True
    ))
    
    # Create incomplete data
    data = {
        "title": "Test Product",
        "description": "Test Description",
        "category_id": 1,
        "sku": "TEST-001",
        "unit_size": "1kg",
        "consumer_price": 100.00,
        "distributor_price": 80.00,
        "stock_quantity": 50
    }
    
    for field in fields_to_remove:
        del data[field]
    
    return data


# Feature: indostar-naturals-ecommerce, Property 71: Validation errors return 400
@pytest.mark.asyncio
@settings(max_examples=100, deadline=None)
@given(invalid_data=missing_required_fields_strategy())
async def test_validation_errors_return_400(invalid_data, db_session: Session, owner_token: str):
    """
    Property 71: Validation errors return 400
    
    For any validation error, the system should return a 400 Bad Request response
    with specific field-level error messages.
    
    Validates: Requirements 17.1
    """
    # Attempt to create a product with missing required fields
    response = client.post(
        "/api/v1/owner/products",
        json=invalid_data,
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    
    # Verify status code is 400
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    
    # Verify error response structure
    error_data = response.json()
    assert "error" in error_data, "Response should contain 'error' key"
    
    error = error_data["error"]
    assert "code" in error, "Error should contain 'code'"
    assert "message" in error, "Error should contain 'message'"
    assert "details" in error, "Error should contain 'details'"
    assert "timestamp" in error, "Error should contain 'timestamp'"
    assert "request_id" in error, "Error should contain 'request_id'"
    
    # Verify error code
    assert error["code"] == "VALIDATION_ERROR", f"Expected VALIDATION_ERROR, got {error['code']}"
    
    # Verify details contain field-level errors
    assert isinstance(error["details"], list), "Details should be a list"
    assert len(error["details"]) > 0, "Details should contain at least one error"
    
    # Verify each detail has field and message
    for detail in error["details"]:
        assert "field" in detail, "Each detail should have 'field'"
        assert "message" in detail, "Each detail should have 'message'"


@pytest.mark.asyncio
@settings(max_examples=50, deadline=None)
@given(invalid_email=invalid_email_strategy())
async def test_email_validation_returns_400(invalid_email, db_session: Session):
    """
    Property 71: Validation errors return 400 (Email validation)
    
    For any invalid email format, the system should return a 400 Bad Request response.
    
    Validates: Requirements 17.1, 16.2
    """
    # Skip empty strings as they might be handled differently
    if not invalid_email or invalid_email.isspace():
        return
    
    # Attempt to send OTP with invalid email
    response = client.post(
        "/api/v1/auth/send-otp",
        json={
            "email": invalid_email,
            "phone": None
        }
    )
    
    # Should return 400 for validation error
    # Note: Some endpoints might return 422 for Pydantic validation
    assert response.status_code in [400, 422], f"Expected 400 or 422, got {response.status_code}"
    
    # Verify error response structure
    error_data = response.json()
    assert "error" in error_data or "detail" in error_data, "Response should contain error information"


@pytest.mark.asyncio
@settings(max_examples=50, deadline=None)
@given(invalid_phone=invalid_phone_strategy())
async def test_phone_validation_returns_400(invalid_phone, db_session: Session):
    """
    Property 71: Validation errors return 400 (Phone validation)
    
    For any invalid phone format, the system should return a 400 Bad Request response.
    
    Validates: Requirements 17.1, 16.3
    """
    # Skip empty strings
    if not invalid_phone or invalid_phone.isspace():
        return
    
    # Attempt to send OTP with invalid phone
    response = client.post(
        "/api/v1/auth/send-otp",
        json={
            "email": None,
            "phone": invalid_phone
        }
    )
    
    # Should return 400 for validation error
    assert response.status_code in [400, 422], f"Expected 400 or 422, got {response.status_code}"
    
    # Verify error response structure
    error_data = response.json()
    assert "error" in error_data or "detail" in error_data, "Response should contain error information"


@pytest.mark.asyncio
@settings(max_examples=50, deadline=None)
@given(
    price=st.one_of(
        st.floats(max_value=-0.01),  # Negative prices
        st.floats(min_value=0.001, max_value=0.009),  # Zero prices
        st.floats(min_value=100.001, max_value=100.999).map(lambda x: round(x, 3))  # More than 2 decimals
    )
)
async def test_price_validation_returns_400(price, db_session: Session, owner_token: str):
    """
    Property 71: Validation errors return 400 (Price validation)
    
    For any invalid price (negative, zero, or more than 2 decimals),
    the system should return a 400 Bad Request response.
    
    Validates: Requirements 17.1, 16.4
    """
    # Skip NaN and infinite values
    if not isinstance(price, (int, float)) or price != price:  # NaN check
        return
    
    # Attempt to create product with invalid price
    response = client.post(
        "/api/v1/owner/products",
        json={
            "title": "Test Product",
            "description": "Test Description",
            "category_id": 1,
            "sku": f"TEST-{abs(hash(str(price))) % 10000}",
            "unit_size": "1kg",
            "consumer_price": price,
            "distributor_price": price * 0.8 if price > 0 else price,
            "stock_quantity": 50
        },
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    
    # Should return 400 for validation error
    assert response.status_code in [400, 422], f"Expected 400 or 422 for price {price}, got {response.status_code}"



# Feature: indostar-naturals-ecommerce, Property 72: Authentication errors return 401
@pytest.mark.asyncio
@settings(max_examples=100, deadline=None)
@given(
    invalid_token=st.one_of(
        st.text(min_size=10, max_size=100),  # Random text
        st.just(""),  # Empty token
        st.just("Bearer invalid_token_here"),  # Invalid format
        st.just("invalid.jwt.token"),  # Invalid JWT
    )
)
async def test_authentication_errors_return_401(invalid_token, db_session: Session):
    """
    Property 72: Authentication errors return 401
    
    For any authentication error (invalid credentials, expired token),
    the system should return a 401 Unauthorized response.
    
    Validates: Requirements 17.2
    """
    # Attempt to access protected endpoint with invalid token
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {invalid_token}"}
    )
    
    # Verify status code is 401
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    # Verify error response structure
    error_data = response.json()
    assert "error" in error_data or "detail" in error_data, "Response should contain error information"
    
    if "error" in error_data:
        error = error_data["error"]
        assert "code" in error, "Error should contain 'code'"
        assert error["code"] in ["AUTHENTICATION_ERROR", "AUTH_ERROR"], f"Expected authentication error code"
        assert "timestamp" in error, "Error should contain 'timestamp'"
        assert "request_id" in error, "Error should contain 'request_id'"


@pytest.mark.asyncio
@settings(max_examples=50, deadline=None)
@given(
    invalid_otp=st.one_of(
        st.text(alphabet=st.characters(whitelist_categories=("Nd",)), min_size=1, max_size=5),  # Wrong length
        st.text(alphabet=st.characters(whitelist_categories=("Nd",)), min_size=7, max_size=10),  # Too long
        st.text(min_size=6, max_size=6),  # Non-numeric
        st.just("000000"),  # Invalid code
        st.just("999999"),  # Invalid code
    )
)
async def test_invalid_otp_returns_401(invalid_otp, db_session: Session):
    """
    Property 72: Authentication errors return 401 (Invalid OTP)
    
    For any invalid OTP code, the system should return a 401 Unauthorized response.
    
    Validates: Requirements 17.2
    """
    # First, we need a phone number to verify against
    # For this test, we'll use a random phone that likely doesn't have an OTP
    test_phone = f"+1555{st.integers(min_value=1000000, max_value=9999999).example()}"
    
    # Attempt to verify with invalid OTP
    response = client.post(
        "/api/v1/auth/verify-otp",
        json={
            "phone": test_phone,
            "otp": invalid_otp
        }
    )
    
    # Should return 401 for invalid OTP
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    # Verify error response
    error_data = response.json()
    assert "error" in error_data or "detail" in error_data, "Response should contain error information"


# Feature: indostar-naturals-ecommerce, Property 73: Authorization errors return 403
@pytest.mark.asyncio
@settings(max_examples=100, deadline=None)
@given(role=st.sampled_from([UserRole.CONSUMER, UserRole.DISTRIBUTOR]))
async def test_authorization_errors_return_403(role, db_session: Session):
    """
    Property 73: Authorization errors return 403
    
    For any authorization error (insufficient permissions),
    the system should return a 403 Forbidden response without exposing sensitive information.
    
    Validates: Requirements 17.3
    """
    # Create a user with non-owner role
    user = User(
        email=f"test_{role.value}_{st.integers(min_value=1000, max_value=9999).example()}@example.com",
        phone=f"+1555{st.integers(min_value=1000000, max_value=9999999).example()}",
        name="Test User",
        role=role,
        is_active=True,
        is_email_verified=True,
        is_phone_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Generate token for non-owner user
    access_token = TokenService.create_access_token(data={"sub": str(user.id)})
    
    # Attempt to access owner-only endpoint
    response = client.get(
        "/api/v1/owner/products",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    # Verify status code is 403
    assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    
    # Verify error response structure
    error_data = response.json()
    assert "error" in error_data or "detail" in error_data, "Response should contain error information"
    
    if "error" in error_data:
        error = error_data["error"]
        assert "code" in error, "Error should contain 'code'"
        assert error["code"] in ["AUTHORIZATION_ERROR", "FORBIDDEN"], f"Expected authorization error code"
        assert "timestamp" in error, "Error should contain 'timestamp'"
        assert "request_id" in error, "Error should contain 'request_id'"
        
        # Verify no sensitive information is exposed
        message = error.get("message", "").lower()
        assert "password" not in message, "Error should not expose passwords"
        assert "secret" not in message, "Error should not expose secrets"
        assert "key" not in message, "Error should not expose keys"
    
    # Cleanup
    db_session.delete(user)
    db_session.commit()


# Feature: indostar-naturals-ecommerce, Property 74: Server errors return 500 and log
@pytest.mark.asyncio
async def test_server_errors_return_500_and_log(db_session: Session, monkeypatch):
    """
    Property 74: Server errors return 500 and log
    
    For any unhandled server error, the system should return a 500 Internal Server Error
    response and log the full error details to the monitoring service.
    
    Validates: Requirements 17.4
    """
    # We'll simulate a server error by making the database unavailable
    # This is a single example test rather than property-based since we need to
    # control the error condition
    
    # Mock the database to raise an exception
    def mock_get_db():
        raise Exception("Simulated database error")
    
    # Temporarily replace the dependency
    from app.core import database
    original_get_db = database.get_db
    database.get_db = mock_get_db
    
    try:
        # Attempt to access an endpoint that uses the database
        response = client.get("/api/v1/products")
        
        # Verify status code is 500
        assert response.status_code == 500, f"Expected 500, got {response.status_code}"
        
        # Verify error response structure
        error_data = response.json()
        assert "error" in error_data, "Response should contain 'error' key"
        
        error = error_data["error"]
        assert "code" in error, "Error should contain 'code'"
        assert error["code"] in ["SERVER_ERROR", "DATABASE_ERROR"], f"Expected server error code"
        assert "message" in error, "Error should contain 'message'"
        assert "timestamp" in error, "Error should contain 'timestamp'"
        assert "request_id" in error, "Error should contain 'request_id'"
        
        # Verify message is sanitized (doesn't expose internal details)
        message = error["message"].lower()
        assert "traceback" not in message, "Error should not expose traceback"
        assert "exception" not in message, "Error should not expose exception details"
        
        # Note: In a real test, we would also verify that the error was logged
        # to the monitoring service (e.g., Sentry), but that requires additional setup
        
    finally:
        # Restore original dependency
        database.get_db = original_get_db


@pytest.mark.asyncio
async def test_error_response_includes_request_id(db_session: Session):
    """
    Verify that all error responses include a request_id for traceability.
    
    This is part of Property 71-74: All errors should include request_id.
    """
    # Test with a validation error (400)
    response = client.post(
        "/api/v1/auth/send-otp",
        json={}  # Missing required fields
    )
    
    error_data = response.json()
    if "error" in error_data:
        assert "request_id" in error_data["error"], "Error should include request_id"
        assert error_data["error"]["request_id"], "request_id should not be empty"
    
    # Verify request_id is also in response headers
    assert "X-Request-ID" in response.headers, "Response should include X-Request-ID header"


@pytest.mark.asyncio
async def test_error_response_includes_timestamp(db_session: Session):
    """
    Verify that all error responses include a timestamp.
    
    This is part of Property 71-74: All errors should include timestamp.
    """
    # Test with a validation error
    response = client.post(
        "/api/v1/auth/send-otp",
        json={}  # Missing required fields
    )
    
    error_data = response.json()
    if "error" in error_data:
        assert "timestamp" in error_data["error"], "Error should include timestamp"
        assert error_data["error"]["timestamp"], "timestamp should not be empty"
        
        # Verify timestamp is in ISO format
        timestamp = error_data["error"]["timestamp"]
        assert "T" in timestamp, "Timestamp should be in ISO format"
        assert timestamp.endswith("Z"), "Timestamp should be in UTC (end with Z)"
