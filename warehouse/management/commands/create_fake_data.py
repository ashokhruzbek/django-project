from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from warehouse.models import Category, Product, Supplier, Order, OrderItem, Inventory
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Creates fake data for testing'

    def handle(self, *args, **kwargs):
        # Create superuser if not exists
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')

        # Create categories
        categories = [
            'Men\'s Clothing',
            'Women\'s Clothing',
            'Children\'s Clothing',
            'Accessories',
            'Footwear'
        ]
        
        for cat_name in categories:
            Category.objects.get_or_create(
                name=cat_name,
                defaults={'description': f'All types of {cat_name.lower()}'}
            )

        # Create products
        products_data = [
            # Men's Clothing
            ('Classic Cotton T-Shirt', 'Men\'s Clothing', 'M-TS001', 'Premium cotton t-shirt', 50, 19.99),
            ('Slim Fit Jeans', 'Men\'s Clothing', 'M-JN001', 'Comfortable slim fit jeans', 30, 49.99),
            ('Business Suit', 'Men\'s Clothing', 'M-ST001', 'Professional business suit', 15, 299.99),
            
            # Women's Clothing
            ('Summer Dress', 'Women\'s Clothing', 'W-DR001', 'Light and stylish summer dress', 40, 39.99),
            ('Yoga Pants', 'Women\'s Clothing', 'W-YP001', 'High-quality yoga pants', 45, 29.99),
            ('Blouse', 'Women\'s Clothing', 'W-BL001', 'Elegant office blouse', 35, 34.99),
            
            # Children's Clothing
            ('Kids T-Shirt', 'Children\'s Clothing', 'C-TS001', 'Colorful kids t-shirt', 60, 14.99),
            ('School Uniform', 'Children\'s Clothing', 'C-UN001', 'Standard school uniform', 40, 44.99),
            
            # Accessories
            ('Leather Belt', 'Accessories', 'A-BT001', 'Genuine leather belt', 25, 24.99),
            ('Winter Scarf', 'Accessories', 'A-SC001', 'Warm winter scarf', 30, 19.99),
            
            # Footwear
            ('Running Shoes', 'Footwear', 'F-SH001', 'Professional running shoes', 20, 89.99),
            ('Casual Sneakers', 'Footwear', 'F-SN001', 'Comfortable casual sneakers', 25, 59.99),
        ]

        for name, cat_name, sku, desc, qty, price in products_data:
            category = Category.objects.get(name=cat_name)
            Product.objects.get_or_create(
                sku=sku,
                defaults={
                    'name': name,
                    'category': category,
                    'description': desc,
                    'quantity': qty,
                    'unit_price': Decimal(str(price))
                }
            )

        # Create suppliers
        suppliers_data = [
            ('Fashion Hub Ltd.', 'John Smith', 'john@fashionhub.com', '+1234567890', '123 Fashion St, NY'),
            ('Style Masters Co.', 'Emma Brown', 'emma@stylemasters.com', '+1987654321', '456 Style Ave, LA'),
            ('Kids Fashion World', 'Mike Johnson', 'mike@kidsfashion.com', '+1122334455', '789 Kids Blvd, CH')
        ]

        for name, contact, email, phone, address in suppliers_data:
            Supplier.objects.get_or_create(
                email=email,
                defaults={
                    'name': name,
                    'contact_person': contact,
                    'phone': phone,
                    'address': address
                }
            )

        # Create orders and order items
        suppliers = list(Supplier.objects.all())
        products = list(Product.objects.all())
        admin_user = User.objects.get(username='admin')

        for i in range(1, 6):
            order = Order.objects.create(
                order_number=f'ORD-2025{i:03d}',
                supplier=random.choice(suppliers),
                status=random.choice(['pending', 'processing', 'completed']),
                created_by=admin_user
            )

            # Add 2-4 random products to each order
            for _ in range(random.randint(2, 4)):
                product = random.choice(products)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=random.randint(5, 20),
                    unit_price=product.unit_price
                )

        # Create inventory records
        locations = ['Main Warehouse', 'Store Room A', 'Store Room B']
        
        for product in products:
            for location in locations:
                if random.random() > 0.5:  # 50% chance to create inventory record
                    Inventory.objects.create(
                        product=product,
                        quantity=random.randint(5, 50),
                        location=location
                    )

        self.stdout.write(self.style.SUCCESS('Successfully created fake data')) 