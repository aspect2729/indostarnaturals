"""Test data factories using Factory Boy"""
import factory
from factory import Faker, SubFactory, LazyAttribute
from factory.alchemy import SQLAlchemyModelFactory
from app.models import (
    User, Product, Category, Cart, CartItem, Order, OrderItem,
    Address, Subscription, Payment, AuditLog
)
from app.models.enums import (
    UserRole, OrderStatus, PaymentStatus, SubscriptionStatus, SubscriptionFrequency
)
from decimal import Decimal
from datetime import datetime, date


class BaseFactory(SQLAlchemyModelFactory):
    """Base factory with common configuration"""
    class Meta:
        abstract = True
        sqlalchemy_session_persistence = "commit"


class UserFactory(BaseFactory):
    """Factory for User model"""
    class Meta:
        model = User
    
    email = Faker('email')
    phone = Faker('phone_number')
    name = Faker('name')
    role = UserRole.CONSUMER
    hashed_password = 'hashed_password'
    is_active = True
    is_email_verified = True
    is_phone_verified = True


class CategoryFactory(BaseFactory):
    """Factory for Category model"""
    class Meta:
        model = Category
    
    name = Faker('word')
    slug = LazyAttribute(lambda obj: obj.name.lower().replace(' ', '-'))
    display_order = Faker('random_int', min=1, max=100)


class ProductFactory(BaseFactory):
    """Factory for Product model"""
    class Meta:
        model = Product
    
    owner_id = 1
    title = Faker('sentence', nb_words=3)
    description = Faker('text', max_nb_chars=200)
    category_id = 1
    sku = Faker('bothify', text='SKU-####')
    unit_size = '1 Unit'
    consumer_price = LazyAttribute(lambda _: Decimal(str(factory.Faker('random_int', min=50, max=500).generate({}))))
    distributor_price = LazyAttribute(lambda obj: obj.consumer_price * Decimal('0.8'))
    stock_quantity = Faker('random_int', min=0, max=100)
    is_active = True
    is_subscription_available = False


class AddressFactory(BaseFactory):
    """Factory for Address model"""
    class Meta:
        model = Address
    
    user_id = 1
    name = Faker('name')
    phone = Faker('phone_number')
    address_line1 = Faker('street_address')
    address_line2 = Faker('secondary_address')
    city = Faker('city')
    state = Faker('state')
    postal_code = Faker('postcode')
    country = 'India'
    is_default = False


class CartFactory(BaseFactory):
    """Factory for Cart model"""
    class Meta:
        model = Cart
    
    user_id = 1
    discount_amount = Decimal('0.00')


class CartItemFactory(BaseFactory):
    """Factory for CartItem model"""
    class Meta:
        model = CartItem
    
    cart_id = 1
    product_id = 1
    quantity = Faker('random_int', min=1, max=10)
    unit_price = LazyAttribute(lambda _: Decimal(str(factory.Faker('random_int', min=50, max=500).generate({}))))


class OrderFactory(BaseFactory):
    """Factory for Order model"""
    class Meta:
        model = Order
    
    user_id = 1
    order_number = LazyAttribute(lambda _: f"ORD-{datetime.now().strftime('%Y%m%d')}-{factory.Faker('random_int', min=1000, max=9999).generate({})}")
    total_amount = LazyAttribute(lambda _: Decimal(str(factory.Faker('random_int', min=100, max=5000).generate({}))))
    discount_amount = Decimal('0.00')
    final_amount = LazyAttribute(lambda obj: obj.total_amount - obj.discount_amount)
    payment_status = PaymentStatus.PENDING
    order_status = OrderStatus.PENDING
    delivery_address_id = 1


class OrderItemFactory(BaseFactory):
    """Factory for OrderItem model"""
    class Meta:
        model = OrderItem
    
    order_id = 1
    product_id = 1
    quantity = Faker('random_int', min=1, max=10)
    unit_price = LazyAttribute(lambda _: Decimal(str(factory.Faker('random_int', min=50, max=500).generate({}))))
    total_price = LazyAttribute(lambda obj: obj.unit_price * obj.quantity)


class SubscriptionFactory(BaseFactory):
    """Factory for Subscription model"""
    class Meta:
        model = Subscription
    
    user_id = 1
    product_id = 1
    razorpay_subscription_id = Faker('bothify', text='sub_????????????')
    plan_frequency = SubscriptionFrequency.DAILY
    start_date = LazyAttribute(lambda _: date.today())
    next_delivery_date = LazyAttribute(lambda _: date.today())
    delivery_address_id = 1
    status = SubscriptionStatus.ACTIVE


class PaymentFactory(BaseFactory):
    """Factory for Payment model"""
    class Meta:
        model = Payment
    
    order_id = 1
    razorpay_payment_id = Faker('bothify', text='pay_????????????')
    razorpay_order_id = Faker('bothify', text='order_????????????')
    amount = LazyAttribute(lambda _: Decimal(str(factory.Faker('random_int', min=100, max=5000).generate({}))))
    currency = 'INR'
    status = PaymentStatus.PENDING


class AuditLogFactory(BaseFactory):
    """Factory for AuditLog model"""
    class Meta:
        model = AuditLog
    
    actor_id = 1
    action_type = 'TEST_ACTION'
    object_type = 'TEST_OBJECT'
    object_id = 1
    details = {}
    ip_address = Faker('ipv4')
