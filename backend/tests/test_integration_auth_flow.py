"""Integration tests for authentication flow"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestAuthenticationFlow:
    """Integration tests for complete authentication flows"""

    def test_otp_authentication_flow(self, client, mock_sms_service):
        """Test complete OTP authentication flow"""
        phone = "+919876543210"
        
        # Step 1: Send OTP
        response = client.post(
            "/api/v1/auth/send-otp",
            json={"phone": phone}
        )
        assert response.status_code == 200
        
        # Step 2: Verify OTP (mocked)
        response = client.post(
            "/api/v1/auth/verify-otp",
            json={"phone": phone, "otp": "123456"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_token_refresh_flow(self, client, test_user):
        """Test token refresh flow"""
        # Get initial tokens
        response = client.post(
            "/api/v1/auth/verify-otp",
            json={"phone": test_user.phone, "otp": "123456"}
        )
        refresh_token = response.json()["refresh_token"]
        
        # Refresh token
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_password_reset_flow(self, client, test_user, mock_email_service):
        """Test complete password reset flow"""
        # Step 1: Request password reset
        response = client.post(
            "/api/v1/auth/reset-password",
            json={"email": test_user.email}
        )
        assert response.status_code == 200
        
        # Step 2: Complete password reset (with mocked token)
        response = client.put(
            "/api/v1/auth/reset-password",
            json={
                "token": "mock_reset_token",
                "new_password": "NewPassword123!"
            }
        )
        assert response.status_code == 200
