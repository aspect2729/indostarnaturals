"""Integration tests for cart to order flow"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestCartToOrderFlow:
    """Integration tests for complete cart to order flow"""

    def test_complete_checkout_flow(self, client, test_user, test_product, test_address, mock_razorpay_client):
        """Test complete flow from adding to cart to creating order"""
        # Step 1: Add item to cart
        response = client.post(
            "/api/v1/cart/items",
            json={
                "product_id": test_product.id,
                "quantity": 2
            },
            headers={"Authorization": f"Bearer mock_token"}
        )
        assert response.status_code == 200
        cart = response.json()
        assert len(cart["items"]) > 0
        
        # Step 2: Apply coupon (optional)
        response = client.post(
            "/api/v1/cart/coupon",
            json={"coupon_code": "TEST10"},
            headers={"Authorization": f"Bearer mock_token"}
        )
        # May succeed or fail depending on coupon validity
        
        # Step 3: Create order
        response = client.post(
            "/api/v1/orders",
            json={"address_id": test_address.id},
            headers={"Authorization": f"Bearer mock_token"}
        )
        assert response.status_code == 200
        order = response.json()
        assert "razorpay_order_id" in order
        assert order["order_status"] == "pending"

    def test_cart_validation_before_checkout(self, client, test_user, test_product, test_address, db_session):
        """Test that cart is validated before checkout"""
        # Add item to cart
        client.post(
            "/api/v1/cart/items",
            json={"product_id": test_product.id, "quantity": 100},
            headers={"Authorization": f"Bearer mock_token"}
        )
        
        # Reduce stock to make cart invalid
        test_product.stock_quantity = 5
        db_session.commit()
        
        # Try to create order - should fail
        response = client.post(
            "/api/v1/orders",
            json={"address_id": test_address.id},
            headers={"Authorization": f"Bearer mock_token"}
        )
        assert response.status_code == 400
        assert "insufficient stock" in response.json()["error"]["message"].lower()
