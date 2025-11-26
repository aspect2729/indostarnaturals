"""Integration tests for webhook processing"""
import pytest
import hmac
import hashlib
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestWebhookProcessing:
    """Integration tests for Razorpay webhook processing"""

    def test_payment_success_webhook(self, client, test_order, db_session):
        """Test processing successful payment webhook"""
        payload = {
            "event": "payment.captured",
            "payload": {
                "payment": {
                    "entity": {
                        "id": "pay_test123",
                        "order_id": test_order.order_number,
                        "amount": int(test_order.final_amount * 100),
                        "status": "captured"
                    }
                }
            }
        }
        
        # Generate signature
        signature = self._generate_webhook_signature(payload)
        
        response = client.post(
            "/api/v1/webhooks/razorpay",
            json=payload,
            headers={"X-Razorpay-Signature": signature}
        )
        
        assert response.status_code == 200
        
        # Verify order status updated
        db_session.refresh(test_order)
        assert test_order.payment_status == "paid"

    def test_payment_failed_webhook(self, client, test_order, db_session):
        """Test processing failed payment webhook"""
        payload = {
            "event": "payment.failed",
            "payload": {
                "payment": {
                    "entity": {
                        "id": "pay_test123",
                        "order_id": test_order.order_number,
                        "status": "failed"
                    }
                }
            }
        }
        
        signature = self._generate_webhook_signature(payload)
        
        response = client.post(
            "/api/v1/webhooks/razorpay",
            json=payload,
            headers={"X-Razorpay-Signature": signature}
        )
        
        assert response.status_code == 200
        
        # Verify order status updated
        db_session.refresh(test_order)
        assert test_order.payment_status == "failed"

    def test_webhook_signature_verification(self, client):
        """Test that webhooks without valid signature are rejected"""
        payload = {
            "event": "payment.captured",
            "payload": {}
        }
        
        response = client.post(
            "/api/v1/webhooks/razorpay",
            json=payload,
            headers={"X-Razorpay-Signature": "invalid_signature"}
        )
        
        assert response.status_code == 401

    def _generate_webhook_signature(self, payload):
        """Generate mock webhook signature"""
        import json
        secret = "test_webhook"
        message = json.dumps(payload).encode()
        signature = hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()
        return signature
