from app.core.database import SessionLocal
from app.models.product import Product
from app.models.product_image import ProductImage
from app.models.category import Category

session = SessionLocal()

# Create categories
categories = {
    "Milk": Category(name="Milk", slug="milk", display_order=1),
    "Dairy Products": Category(name="Dairy Products", slug="dairy", display_order=2)
}

for name, cat in categories.items():
    existing = session.query(Category).filter(Category.slug == cat.slug).first()
    if not existing:
        session.add(cat)
        session.flush()
        print(f"Created category: {name}")
    else:
        categories[name] = existing
        print(f"Category exists: {name}")

session.commit()

# Create products
products_data = [
    {
        "title": "Organic Full Cream Milk",
        "description": "Fresh organic full cream milk from grass-fed cows. Rich, creamy, and nutritious.",
        "category": "Milk",
        "sku": "MLK-FCM-001",
        "unit_size": "1 Liter",
        "consumer_price": 60.00,
        "distributor_price": 50.00,
        "stock_quantity": 200,
        "images": [
            "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=800",
            "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=800"
        ]
    },
    {
        "title": "Organic Toned Milk",
        "description": "Healthy organic toned milk with reduced fat content.",
        "category": "Milk",
        "sku": "MLK-TON-001",
        "unit_size": "1 Liter",
        "consumer_price": 50.00,
        "distributor_price": 42.00,
        "stock_quantity": 250,
        "images": [
            "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=800",
            "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=800"
        ]
    },
    {
        "title": "Fresh Yogurt (Dahi)",
        "description": "Creamy organic yogurt made from fresh milk. Rich in probiotics.",
        "category": "Dairy Products",
        "sku": "DRY-YOG-001",
        "unit_size": "500 grams",
        "consumer_price": 40.00,
        "distributor_price": 35.00,
        "stock_quantity": 80,
        "images": [
            "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=800",
            "https://images.unsplash.com/photo-1571212515416-fca2ce42e1b7?w=800"
        ]
    },
    {
        "title": "Pure Desi Ghee",
        "description": "Traditional pure desi ghee made from organic butter. Rich aroma and authentic taste.",
        "category": "Dairy Products",
        "sku": "DRY-GHE-001",
        "unit_size": "1 KG",
        "consumer_price": 600.00,
        "distributor_price": 550.00,
        "stock_quantity": 50,
        "images": [
            "https://images.unsplash.com/photo-1628088062854-d1870b4553da?w=800",
            "https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=800"
        ]
    },
    {
        "title": "Organic Butter",
        "description": "Fresh organic butter churned from pure cream. Unsalted and perfect for spreading.",
        "category": "Dairy Products",
        "sku": "DRY-BUT-001",
        "unit_size": "500 grams",
        "consumer_price": 250.00,
        "distributor_price": 220.00,
        "stock_quantity": 60,
        "images": [
            "https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=800",
            "https://images.unsplash.com/photo-1628088062854-d1870b4553da?w=800"
        ]
    },
    {
        "title": "Paneer (Cottage Cheese)",
        "description": "Fresh organic paneer made from pure milk. Soft, fresh, and protein-rich.",
        "category": "Dairy Products",
        "sku": "DRY-PAN-001",
        "unit_size": "500 grams",
        "consumer_price": 175.00,
        "distributor_price": 150.00,
        "stock_quantity": 40,
        "images": [
            "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=800",
            "https://images.unsplash.com/photo-1628088062854-d1870b4553da?w=800"
        ]
    }
]

for pd in products_data:
    existing = session.query(Product).filter(Product.sku == pd["sku"]).first()
    if existing:
        print(f"Product exists: {pd['title']}")
        continue
    
    product = Product(
        owner_id=1,
        title=pd["title"],
        description=pd["description"],
        category_id=categories[pd["category"]].id,
        sku=pd["sku"],
        unit_size=pd["unit_size"],
        consumer_price=pd["consumer_price"],
        distributor_price=pd["distributor_price"],
        stock_quantity=pd["stock_quantity"],
        is_subscription_available=True,
        is_active=True
    )
    session.add(product)
    session.flush()
    
    for idx, url in enumerate(pd["images"]):
        img = ProductImage(product_id=product.id, url=url, alt_text=pd["title"], display_order=idx)
        session.add(img)
    
    print(f"Created: {pd['title']}")

session.commit()
session.close()
print("\n✅ Done! Products added successfully!")
