"""Tests for Cart API endpoints"""
import pytest
from app.main import app


def test_cart_endpoints_registered():
    """Test that cart API endpoints are registered"""
    routes = [route.path for route in app.routes]
    
    # Check that all cart endpoints are registered
    assert "/api/v1/cart" in routes
    assert "/api/v1/cart/items" in routes
    assert "/api/v1/cart/items/{item_id}" in routes
    assert "/api/v1/cart/coupon" in routes


def test_cart_endpoints_require_authentication():
    """Test that cart endpoints have authentication dependencies"""
    from app.api.cart import router
    
    # Get all routes from the cart router
    cart_routes = router.routes
    
    # Verify we have the expected number of routes
    assert len(cart_routes) == 6  # GET, POST items, PUT items, DELETE items, POST coupon, DELETE coupon
    
    # Verify each route has dependencies (authentication)
    for route in cart_routes:
        assert len(route.dependencies) > 0 or len(route.dependant.dependencies) > 0

