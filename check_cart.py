import sys
sys.path.insert(0, 'backend')

from app.core.database import SessionLocal
from app.models.cart import Cart
from app.models.cart_item import CartItem

db = SessionLocal()
cart = db.query(Cart).filter(Cart.user_id == 1).first()

if cart:
    print(f"Cart ID: {cart.id}")
    print(f"Items: {len(cart.items)}")
    for item in cart.items:
        print(f"  - Product ID: {item.product_id}, Qty: {item.quantity}, Price: {item.unit_price}")
        if item.product:
            print(f"    Product: {item.product.title}, Stock: {item.product.stock_quantity}")
        else:
            print(f"    Product: NOT FOUND")
else:
    print("No cart found")

db.close()
