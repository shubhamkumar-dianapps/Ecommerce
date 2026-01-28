"""
Seed Products Command

Creates realistic sample data for testing:
- 5 Shopkeepers (verified)
- 10 Categories
- 15 Brands
- 50 Products (10-12 per shopkeeper)
- Product images
- Inventory data
"""

from decimal import Decimal
from typing import List, Tuple
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.accounts.models import User, ShopKeeperProfile
from apps.products.models import Category, Brand, Product, ProductImage, Inventory


class Command(BaseCommand):
    help = "Seed database with realistic product data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing products before seeding",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Clearing existing data...")
            Product.objects.all().delete()
            Category.objects.all().delete()
            Brand.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("[OK] Cleared existing data"))

        self.stdout.write("Starting seed process...")

        with transaction.atomic():
            # Create shopkeepers
            shopkeepers = self.create_shopkeepers()
            self.stdout.write(
                self.style.SUCCESS(f"[OK] Created {len(shopkeepers)} shopkeepers")
            )

            # Create categories
            categories = self.create_categories()
            self.stdout.write(
                self.style.SUCCESS(f"[OK] Created {len(categories)} categories")
            )

            # Create brands
            brands = self.create_brands()
            self.stdout.write(self.style.SUCCESS(f"[OK] Created {len(brands)} brands"))

            # Create products
            products = self.create_products(shopkeepers, categories, brands)
            self.stdout.write(self.style.SUCCESS(f"[OK] Created {len(products)} products"))

            # Create inventory
            self.create_inventory(products)
            self.stdout.write(
                self.style.SUCCESS(f"[OK] Created inventory for {len(products)} products")
            )

        self.stdout.write(self.style.SUCCESS("\n[SUCCESS] Seeding completed successfully!"))
        self.stdout.write(f"\nSummary:")
        self.stdout.write(f"  Shopkeepers: {len(shopkeepers)}")
        self.stdout.write(f"  Categories: {len(categories)}")
        self.stdout.write(f"  Brands: {len(brands)}")
        self.stdout.write(f"  Products: {len(products)}")

    def create_shopkeepers(self) -> List[User]:
        """Create 5 verified shopkeepers"""
        shopkeepers_data = [
            {
                "email": "electronics.shop@ecommerce.com",
                "phone": "+919900001111",
                "password": "ShopPass123!",
                "shop_name": "Tech Galaxy",
                "gst_number": "22AAAAA1111A1Z5",
            },
            {
                "email": "fashion.store@ecommerce.com",
                "phone": "+919900002222",
                "password": "ShopPass123!",
                "shop_name": "Fashion Hub",
                "gst_number": "22BBBBB2222B2Z5",
            },
            {
                "email": "home.shop@ecommerce.com",
                "phone": "+919900003333",
                "password": "ShopPass123!",
                "shop_name": "Home Essentials",
                "gst_number": "22CCCCC3333C3Z5",
            },
            {
                "email": "sports.store@ecommerce.com",
                "phone": "+919900004444",
                "password": "ShopPass123!",
                "shop_name": "Sports Arena",
                "gst_number": "22DDDDD4444D4Z5",
            },
            {
                "email": "books.shop@ecommerce.com",
                "phone": "+919900005555",
                "password": "ShopPass123!",
                "shop_name": "Book Paradise",
                "gst_number": "22EEEEE5555E5Z5",
            },
        ]

        shopkeepers = []
        for data in shopkeepers_data:
            # Check if user already exists
            user = User.objects.filter(email=data["email"]).first()
            if not user:
                user = User.objects.create_user(
                    email=data["email"],
                    phone=data["phone"],
                    password=data["password"],
                    role=User.Role.SHOPKEEPER,
                )
                # Update shopkeeper profile
                user.shopkeeperprofile.shop_name = data["shop_name"]
                user.shopkeeperprofile.gst_number = data["gst_number"]
                user.shopkeeperprofile.is_verified = True  # Verify them
                user.shopkeeperprofile.save()
            shopkeepers.append(user)

        return shopkeepers

    def create_categories(self) -> List[Category]:
        """Create product categories"""
        categories_data = [
            ("Electronics", "electronics", "Electronic devices and accessories"),
            ("Fashion", "fashion", "Clothing and fashion accessories"),
            ("Home & Kitchen", "home-kitchen", "Home and kitchen essentials"),
            ("Sports & Fitness", "sports-fitness", "Sports equipment and fitness gear"),
            ("Books", "books", "Books and educational materials"),
            (
                "Beauty & Personal Care",
                "beauty-care",
                "Beauty and personal care products",
            ),
            ("Toys & Games", "toys-games", "Toys and gaming products"),
            ("Automotive", "automotive", "Automotive parts and accessories"),
            ("Health & Wellness", "health-wellness", "Health and wellness products"),
            ("Furniture", "furniture", "Home and office furniture"),
        ]

        categories = []
        for name, slug, desc in categories_data:
            category, created = Category.objects.get_or_create(
                slug=slug,
                defaults={"name": name, "description": desc, "is_active": True},
            )
            categories.append(category)

        return categories

    def create_brands(self) -> List[Brand]:
        """Create product brands"""
        brands_data = [
            ("Apple", "apple", "Premium technology products"),
            ("Samsung", "samsung", "Electronics and home appliances"),
            ("Nike", "nike", "Sports and athletic wear"),
            ("Adidas", "adidas", "Sports equipment and apparel"),
            ("Sony", "sony", "Electronics and entertainment"),
            ("LG", "lg", "Home appliances and electronics"),
            ("Puma", "puma", "Sports and lifestyle brand"),
            ("Philips", "philips", "Health and lifestyle electronics"),
            ("Boat", "boat", "Audio and wearable devices"),
            ("Mi", "mi", "Smart devices and electronics"),
            ("Dell", "dell", "Computers and technology"),
            ("HP", "hp", "Computers and printers"),
            ("Lenovo", "lenovo", "Computers and tablets"),
            ("Asus", "asus", "Computer hardware"),
            ("Penguin", "penguin", "Publishing house"),
        ]

        brands = []
        for name, slug, desc in brands_data:
            brand, created = Brand.objects.get_or_create(
                slug=slug,
                defaults={"name": name, "description": desc, "is_active": True},
            )
            brands.append(brand)

        return brands

    def create_products(
        self, shopkeepers: List[User], categories: List[Category], brands: List[Brand]
    ) -> List[Product]:
        """Create 50 realistic products"""

        products_data = [
            # Electronics (Shopkeeper 1 - Tech Galaxy) - 12 products
            (
                "iPhone 14 Pro",
                "iphone-14-pro",
                "Latest iPhone with A16 Bionic chip",
                "Premium smartphone with ProMotion display",
                categories[0],
                brands[0],
                "89999.00",
                "99999.00",
                "75000.00",
                "IPHONE-14-PRO",
                shopkeepers[0],
            ),
            (
                "MacBook Air M2",
                "macbook-air-m2",
                "Thin and light laptop with M2 chip",
                "13-inch laptop with incredible performance",
                categories[0],
                brands[0],
                "119900.00",
                "129900.00",
                "95000.00",
                "MBA-M2-13",
                shopkeepers[0],
            ),
            (
                "Samsung Galaxy S23",
                "samsung-galaxy-s23",
                "Flagship Android smartphone",
                "Premium phone with amazing camera",
                categories[0],
                brands[1],
                "79999.00",
                "89999.00",
                "65000.00",
                "SGS23-256",
                shopkeepers[0],
            ),
            (
                "Sony WH-1000XM5",
                "sony-wh-1000xm5",
                "Premium noise cancelling headphones",
                "Industry-leading noise cancellation",
                categories[0],
                brands[4],
                "29990.00",
                "34990.00",
                "22000.00",
                "SONY-XM5",
                shopkeepers[0],
            ),
            (
                "Dell XPS 15",
                "dell-xps-15",
                "Premium laptop for professionals",
                "15-inch laptop with stunning display",
                categories[0],
                brands[10],
                "154900.00",
                "169900.00",
                "125000.00",
                "DELL-XPS15",
                shopkeepers[0],
            ),
            (
                'Mi Smart TV 55"',
                "mi-smart-tv-55",
                "Large 4K Android TV",
                "Smart TV with built-in Chromecast",
                categories[0],
                brands[9],
                "44999.00",
                "54999.00",
                "35000.00",
                "MI-TV-55",
                shopkeepers[0],
            ),
            (
                "Boat Airdopes 141",
                "boat-airdopes-141",
                "True wireless earbuds",
                "Bluetooth earbuds with great sound",
                categories[0],
                brands[8],
                "1499.00",
                "2499.00",
                "800.00",
                "BOAT-141",
                shopkeepers[0],
            ),
            (
                "HP LaserJet Pro",
                "hp-laserjet-pro",
                "Professional laser printer",
                "Fast and reliable printing",
                categories[0],
                brands[11],
                "18999.00",
                "22999.00",
                "14000.00",
                "HP-LJ-PRO",
                shopkeepers[0],
            ),
            (
                "Lenovo IdeaPad",
                "lenovo-ideapad",
                "Budget-friendly laptop",
                "Great laptop for students",
                categories[0],
                brands[12],
                "45990.00",
                "52990.00",
                "38000.00",
                "LENOVO-IP",
                shopkeepers[0],
            ),
            (
                "Asus ROG Laptop",
                "asus-rog-laptop",
                "Gaming laptop with RTX graphics",
                "High-performance gaming machine",
                categories[0],
                brands[13],
                "124900.00",
                "139900.00",
                "98000.00",
                "ASUS-ROG",
                shopkeepers[0],
            ),
            (
                "LG Refrigerator",
                "lg-refrigerator",
                "Double door frost-free fridge",
                "Energy efficient refrigerator",
                categories[2],
                brands[5],
                "35990.00",
                "42990.00",
                "28000.00",
                "LG-FRIDGE",
                shopkeepers[0],
            ),
            (
                "Philips Air Purifier",
                "philips-air-purifier",
                "HEPA air purifier for home",
                "Clean air for healthy living",
                categories[2],
                brands[7],
                "14999.00",
                "18999.00",
                "11000.00",
                "PHILIPS-AP",
                shopkeepers[0],
            ),
            # Fashion (Shopkeeper 2 - Fashion Hub) - 10 products
            (
                "Nike Air Max 270",
                "nike-air-max-270",
                "Men's running shoes",
                "Comfortable sports shoes with great cushioning",
                categories[1],
                brands[2],
                "12995.00",
                "14995.00",
                "9000.00",
                "NIKE-AM270",
                shopkeepers[1],
            ),
            (
                "Adidas Ultraboost",
                "adidas-ultraboost",
                "Premium running shoes",
                "High-performance running shoes",
                categories[1],
                brands[3],
                "15999.00",
                "17999.00",
                "12000.00",
                "ADIDAS-UB",
                shopkeepers[1],
            ),
            (
                "Puma T-Shirt",
                "puma-tshirt",
                "Men's sports t-shirt",
                "Comfortable cotton t-shirt",
                categories[1],
                brands[6],
                "999.00",
                "1499.00",
                "500.00",
                "PUMA-TSH",
                shopkeepers[1],
            ),
            (
                "Nike Dri-FIT Jersey",
                "nike-drifit-jersey",
                "Sports jersey for training",
                "Moisture-wicking sports wear",
                categories[1],
                brands[2],
                "2495.00",
                "2995.00",
                "1800.00",
                "NIKE-DFJ",
                shopkeepers[1],
            ),
            (
                "Adidas Track Pants",
                "adidas-track-pants",
                "Men's training pants",
                "Comfortable track pants",
                categories[1],
                brands[3],
                "2799.00",
                "3299.00",
                "2000.00",
                "ADIDAS-TP",
                shopkeepers[1],
            ),
            (
                "Puma Backpack",
                "puma-backpack",
                "Sports backpack",
                "Durable backpack for gym",
                categories[1],
                brands[6],
                "1899.00",
                "2499.00",
                "1200.00",
                "PUMA-BP",
                shopkeepers[1],
            ),
            (
                "Nike Sportswear Hoodie",
                "nike-hoodie",
                "Men's fleece hoodie",
                "Warm and comfortable hoodie",
                categories[1],
                brands[2],
                "3995.00",
                "4495.00",
                "2800.00",
                "NIKE-HOOD",
                shopkeepers[1],
            ),
            (
                "Adidas Socks Pack",
                "adidas-socks-pack",
                "Pack of 3 sports socks",
                "Cushioned athletic socks",
                categories[1],
                brands[3],
                "699.00",
                "999.00",
                "400.00",
                "ADIDAS-SCK",
                shopkeepers[1],
            ),
            (
                "Puma Gym Bag",
                "puma-gym-bag",
                "Duffle bag for sports",
                "Spacious gym bag",
                categories[1],
                brands[6],
                "1599.00",
                "1999.00",
                "1000.00",
                "PUMA-GYM",
                shopkeepers[1],
            ),
            (
                "Nike Cap",
                "nike-cap",
                "Sports cap with logo",
                "Adjustable sports cap",
                categories[1],
                brands[2],
                "799.00",
                "1099.00",
                "500.00",
                "NIKE-CAP",
                shopkeepers[1],
            ),
            # Home & Kitchen (Shopkeeper 3 - Home Essentials) - 10 products
            (
                "Philips Air Fryer",
                "philips-air-fryer",
                "Digital air fryer 4.1L",
                "Healthy cooking with less oil",
                categories[2],
                brands[7],
                "8999.00",
                "10999.00",
                "6500.00",
                "PHILIPS-AF",
                shopkeepers[2],
            ),
            (
                "LG Microwave Oven",
                "lg-microwave-oven",
                "Convection microwave",
                "Multi-function microwave oven",
                categories[2],
                brands[5],
                "12990.00",
                "15990.00",
                "9500.00",
                "LG-MWO",
                shopkeepers[2],
            ),
            (
                "Philips Hand Blender",
                "philips-hand-blender",
                "Electric hand blender",
                "Versatile kitchen tool",
                categories[2],
                brands[7],
                "1799.00",
                "2299.00",
                "1200.00",
                "PHILIPS-HB",
                shopkeepers[2],
            ),
            (
                "LG Washing Machine",
                "lg-washing-machine",
                "7kg fully automatic",
                "Energy-efficient washing machine",
                categories[2],
                brands[5],
                "24990.00",
                "29990.00",
                "19000.00",
                "LG-WM-7KG",
                shopkeepers[2],
            ),
            (
                "Philips Iron",
                "philips-iron",
                "Steam iron for clothes",
                "Non-stick steam iron",
                categories[2],
                brands[7],
                "1499.00",
                "1999.00",
                "900.00",
                "PHILIPS-IR",
                shopkeepers[2],
            ),
            (
                "LG Vacuum Cleaner",
                "lg-vacuum-cleaner",
                "Bagless vacuum cleaner",
                "Powerful suction cleaner",
                categories[2],
                brands[5],
                "6999.00",
                "8999.00",
                "5000.00",
                "LG-VC",
                shopkeepers[2],
            ),
            (
                "Philips Water Purifier",
                "philips-water-purifier",
                "RO water purifier",
                "Safe drinking water",
                categories[2],
                brands[7],
                "11999.00",
                "14999.00",
                "8500.00",
                "PHILIPS-WP",
                shopkeepers[2],
            ),
            (
                "LG TV 43 inch",
                "lg-tv-43",
                '43" Full HD Smart TV',
                "Smart TV with webOS",
                categories[0],
                brands[5],
                "32990.00",
                "39990.00",
                "25000.00",
                "LG-TV-43",
                shopkeepers[2],
            ),
            (
                "Philips Kettle",
                "philips-kettle",
                "Electric kettle 1.5L",
                "Fast boiling kettle",
                categories[2],
                brands[7],
                "1299.00",
                "1799.00",
                "800.00",
                "PHILIPS-KT",
                shopkeepers[2],
            ),
            (
                "LG AC 1.5 Ton",
                "lg-ac-15ton",
                "1.5 ton split AC",
                "Energy-saving air conditioner",
                categories[2],
                brands[5],
                "35990.00",
                "42990.00",
                "28000.00",
                "LG-AC-15",
                shopkeepers[2],
            ),
            # Sports & Fitness (Shopkeeper 4 - Sports Arena) - 10 products
            (
                "Nike Football",
                "nike-football",
                "Professional football size 5",
                "Durable football for matches",
                categories[3],
                brands[2],
                "1499.00",
                "1999.00",
                "900.00",
                "NIKE-FB",
                shopkeepers[3],
            ),
            (
                "Adidas Cricket Bat",
                "adidas-cricket-bat",
                "English willow cricket bat",
                "Professional grade bat",
                categories[3],
                brands[3],
                "5999.00",
                "7999.00",
                "4500.00",
                "ADIDAS-CB",
                shopkeepers[3],
            ),
            (
                "Puma Yoga Mat",
                "puma-yoga-mat",
                "Anti-slip yoga mat 6mm",
                "Comfortable yoga mat",
                categories[3],
                brands[6],
                "899.00",
                "1299.00",
                "500.00",
                "PUMA-YM",
                shopkeepers[3],
            ),
            (
                "Nike Gym Gloves",
                "nike-gym-gloves",
                "Weightlifting gloves",
                "Padded gym gloves",
                categories[3],
                brands[2],
                "799.00",
                "1199.00",
                "500.00",
                "NIKE-GG",
                shopkeepers[3],
            ),
            (
                "Adidas Badminton Racket",
                "adidas-badminton",
                "Lightweight badminton racket",
                "Professional racket",
                categories[3],
                brands[3],
                "2499.00",
                "2999.00",
                "1800.00",
                "ADIDAS-BR",
                shopkeepers[3],
            ),
            (
                "Puma Dumbbells Set",
                "puma-dumbbells",
                "10kg dumbbells pair",
                "Cast iron dumbbells",
                categories[3],
                brands[6],
                "1899.00",
                "2499.00",
                "1300.00",
                "PUMA-DB",
                shopkeepers[3],
            ),
            (
                "Nike Running Shorts",
                "nike-running-shorts",
                "Men's running shorts",
                "Lightweight athletic shorts",
                categories[3],
                brands[2],
                "1499.00",
                "1999.00",
                "1000.00",
                "NIKE-RS",
                shopkeepers[3],
            ),
            (
                "Adidas Tennis Racket",
                "adidas-tennis",
                "Professional tennis racket",
                "Graphite tennis racket",
                categories[3],
                brands[3],
                "4999.00",
                "5999.00",
                "3500.00",
                "ADIDAS-TR",
                shopkeepers[3],
            ),
            (
                "Puma Skipping Rope",
                "puma-skipping-rope",
                "Adjustable jump rope",
                "Speed skipping rope",
                categories[3],
                brands[6],
                "399.00",
                "599.00",
                "200.00",
                "PUMA-SR",
                shopkeepers[3],
            ),
            (
                "Nike Resistance Bands",
                "nike-resistance-bands",
                "Set of 5 resistance bands",
                "Exercise bands",
                categories[3],
                brands[2],
                "999.00",
                "1499.00",
                "600.00",
                "NIKE-RB",
                shopkeepers[3],
            ),
            # Books (Shopkeeper 5 - Book Paradise) - 8 products
            (
                "The Alchemist",
                "the-alchemist",
                "Paulo Coelho bestseller",
                "Inspirational fiction novel",
                categories[4],
                brands[14],
                "299.00",
                "399.00",
                "180.00",
                "BOOK-ALC",
                shopkeepers[4],
            ),
            (
                "Atomic Habits",
                "atomic-habits",
                "James Clear self-help book",
                "Guide to building good habits",
                categories[4],
                brands[14],
                "499.00",
                "699.00",
                "350.00",
                "BOOK-AH",
                shopkeepers[4],
            ),
            (
                "Rich Dad Poor Dad",
                "rich-dad-poor-dad",
                "Robert Kiyosaki finance book",
                "Financial literacy classic",
                categories[4],
                brands[14],
                "399.00",
                "499.00",
                "250.00",
                "BOOK-RDPD",
                shopkeepers[4],
            ),
            (
                "Think and Grow Rich",
                "think-grow-rich",
                "Napoleon Hill classic",
                "Success principles book",
                categories[4],
                brands[14],
                "249.00",
                "349.00",
                "150.00",
                "BOOK-TGR",
                shopkeepers[4],
            ),
            (
                "Harry Potter Set",
                "harry-potter-set",
                "Complete 7 book series",
                "JK Rowling fantasy series",
                categories[4],
                brands[14],
                "2999.00",
                "3999.00",
                "2200.00",
                "BOOK-HP-SET",
                shopkeepers[4],
            ),
            (
                "The Monk Who Sold Ferrari",
                "monk-sold-ferrari",
                "Robin Sharma self-help",
                "Life lessons book",
                categories[4],
                brands[14],
                "350.00",
                "450.00",
                "200.00",
                "BOOK-MWSF",
                shopkeepers[4],
            ),
            (
                "Sapiens",
                "sapiens",
                "Yuval Noah Harari history",
                "History of humankind",
                categories[4],
                brands[14],
                "599.00",
                "799.00",
                "400.00",
                "BOOK-SAP",
                shopkeepers[4],
            ),
            (
                "The Psychology of Money",
                "psychology-of-money",
                "Morgan Housel finance book",
                "Understanding money behavior",
                categories[4],
                brands[14],
                "449.00",
                "599.00",
                "300.00",
                "BOOK-POM",
                shopkeepers[4],
            ),
        ]

        products = []
        for (
            name,
            slug,
            desc,
            short_desc,
            category,
            brand,
            price,
            compare_price,
            cost_price,
            sku,
            shopkeeper,
        ) in products_data:
            product, created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "description": desc,
                    "short_description": short_desc,
                    "category": category,
                    "brand": brand,
                    "price": Decimal(price),
                    "compare_at_price": Decimal(compare_price),
                    "cost_price": Decimal(cost_price),
                    "sku": sku,
                    "shopkeeper": shopkeeper,
                    "status": Product.ProductStatus.PUBLISHED,
                    "is_featured": len(products) < 10,  # First 10 are featured
                },
            )
            products.append(product)

        return products

    def create_inventory(self, products: List[Product]) -> None:
        """Create inventory for all products"""
        import random

        for product in products:
            Inventory.objects.get_or_create(
                product=product,
                defaults={
                    "quantity": random.randint(20, 200),
                    "reserved": 0,
                    "low_stock_threshold": 10,
                },
            )
