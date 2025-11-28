"""
Script to add sample products with images to the database
"""
from app.core.database import SessionLocal
from app.models.product import Product
from app.models.product_image import Proge
from app.models.category impoy

# Sample product data
CATEGORIES = [
    {
        "name": "Jaggery",
        "slug": "jaggery"
    },
    {
     lk",
        "slug": "milk"
    },
    {
      ,
     
    }
]

PRODUTS = [
   {
er",
        "des
     gery",
        "sku": "JAG-POW-001",
        "unit_size": "1 KG",
        "consumer_price": 120.00,
        "distributor_pri100.00,
        "stock_quantity": 100,
        "is_subscription_availe,
        "images": [
            {"url": "https://imagder"},
            {"url": "https://images.unspla"}
        ]
    },
    {
        "",
      ",
     
        "sku": "JAG-BLK-001",
        "unit_size": "1 KG",
        "consumer_price": 100.00,
        "distributor_pri
        "stock_quantity": 150,
        "is_subscription_availrue,
        "images": [
            {"url": "https://imageocks"},
            {"url": "https://images.unspla}
        ]
    },
    {
        "ilk",
      y.",
     
        "sku": "MLK-FCM-001",
        "unit_size": "1 Liter",
        "consumer_price": 60,
        "distributor_pr50.00,
        "stock_quantity": 200,
        "is_subscription_avail: True,
        "images": [
            {"url": "https://imag},
            {"url": "https://images.unspla"}
        ]
    },
    {
        "",
      e.",
     ,
        "sku": "MLK-TON-001",
        "unit_size": "1 Liter",
        "consumer_price": 5
        "distributor_pr,
        "stock_quantity": 250,
        "is_subscription_avail
        "images": [
            {"url": "https://imag},
            {"url": "https://images.unsplak"}
        ]
    },
    {
        ")",
      .",
     cts",
        "sku": "DRY-YOG-001",
        "unit_size": "500 grams",
        "consumer_price": 40.00,
        "distributor_pr0,
        "stock_quantity": 80,
        "is_subscription_avaiTrue,
        "images": [
            {"url": "https://imag},
            {"url": "https://images.unspla"}
        ]
    },
    {
        "e",
      
     
        "sku": "DRY-GHE-001",
        "unit_size": "1 KG",
        "consumer_price": 600.00,
        "distributor_pri
        "stock_quantity": 50,
        "is_subscription_avai: False,
        "images": [
            {"url": "https://imag,
            {"url": "https://images.unsplase"}
        ]
    },
    {
        "
      ",
     ,
        "sku": "DRY-BUT-001",
        "unit_size": "500 grams",
        "consumer_price": 250.00,
        "distributor_pri
        "stock_quantity": 60,
        "is_subscription_avai
        "images": [
            {"url": "https://imater"},
            {"url": "https://images.unsplas"}
        ]
    },
    {
        "
      ,
     ,
        "sku": "DRY-PAN-001",
        "unit_size": "500 grams",
        "consumer_price": 175.00,
        "distributor_pri.00,
        "stock_quantity": 40,
        "is_subscription_avai,
        "images": [
            {"url": "https://ima,
            {"url": "https://images.unspla"}
        ]
    },
    {
        "
      .",
     ery",
        "sku": "JAG-LIQ-001",
        "unit_size": "1 Liter",
        "consumer_price": 150.,
        "distributor_pri
        "stock_quantity": 70,
        "is_subscription_avai
        "images": [
            {"url": "https://imag,
            {"url": "https://images.unsplarup"}
        ]
    }
]


d:


    try:
        # Get owner user (assuming ID 1 is th)
        owner_id = 1
        
        # First, create categories
        category_map = {}
        for cat_data in CATEGORIES:
            # Check if category exists
            existing = session.query(Category).filter(Category.slug == cat_data['slug']).first()
            
            if not existing:
                category = Category(
                    name=cat_data["name"],
                    slug=cat_data["slug"],
                    display_order=0
                )
                session.add(category)
                session.flush()
                category_map[cat_data["name"]] = category.id
                print(f"✅ Created category: {cat_data['name']}")
            else:
                category_map[cat_data["name"]] = existing.id
                print(f"ℹ️  Category already exists: {cat_data['name']}")
        
        session.commit()
        
        # Now create products
        for prod_data in PRODUCTS:
            # Check if product exists
            existing = session.query(Product).filter(Product.sku == prod_data['sku']).first()
            
            if existing:
                print(f"ℹ️  Product already exists: {prod_data['title']}"
                continue
            
            # Create product
            product = Product(
                owner_id=owner_id,
                title=prod_data["title"],
                description=prod_data["description"],
                category_id=category_map["]],
                sku=prod_data["sku"],
                unit_size=prod_data["unit_size"],
                consumer_price=prod_data["consumer_price"],
                distributor_price=prod_data["distributor_price"],
                stock_quantity=prod_data["stock_quantity"],
                is_subscriptio,
             e
            )
            session.add(product)
            
            
            # Add images
            for idx, image_data in enumerate(s"]):
                product_image = ProductIma
                    product_id=product.id,
                    url=image_data["url"],
                    alt_text=image_da,
                 
                )
            
            
        ")
        
        session.commit()
        !")
        print(f"\n📊 Summa
        print(f"   - Categ")
        print(f"   - Products: {len
        print(f"\n🌐 Viss!")
        
    except Ex
        sess)
        print(f"❌ Error
back

        raise
    finally:
        session.close()
ts()
ample_producdd_s
    a\n")e...to databasroducts ple pam sAddingnt("🚀 ":
    pri_main__ == "_e__

if __nam