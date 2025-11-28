from app.core.database import SessionLocal
from app.models.product import Product

db = SessionLocal()
products = db.query(Product).all()

print(f"Total products: {len(products)}")
if products:
    p = products[0]
    print(f"\nFirst product:")
    print(f"  Title: {p.title}")
    print(f"  Has stock_quantity: {hasattr(p, 'stock_quantity')}")
    if hasattr(p, 'stock_quantity'):
        print(f"  Stock: {p.stock_quantity}")
    
    # Check all attributes
    print(f"\n  All attributes: {dir(p)}")

db.close()
