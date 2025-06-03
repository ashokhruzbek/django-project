from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from warehouse.models import Category, Product, Supplier, Order, OrderItem, Inventory
from faker import Faker
import random
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Generates fake data for testing'

    def handle(self, *args, **kwargs):
        fake = Faker()
        
        # Create a test user if not exists
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            user.set_password('admin')
            user.save()
            self.stdout.write(f'Created admin user')
        
        # Create categories
        categories = []
        category_names = ['Electronics', 'Clothing', 'Food', 'Furniture', 'Books', 'Sports', 'Toys', 'Tools', 'Health', 'Beauty']
        for name in category_names:
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={'description': fake.text(max_nb_chars=200)}
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {name}')

        # Create suppliers
        suppliers = []
        for _ in range(20):
            supplier = Supplier.objects.create(
                name=fake.company(),
                contact_person=fake.name(),
                email=fake.email(),
                phone=fake.phone_number(),
                address=fake.address()
            )
            suppliers.append(supplier)
            self.stdout.write(f'Created supplier: {supplier.name}')

        # Create products
        products = []
        for _ in range(100):
            sku = fake.unique.random_number(digits=8)
            product = Product.objects.create(
                name=f"{fake.word().title()} {fake.word().title()}",
                category=random.choice(categories),
                sku=str(sku),
                description=fake.text(max_nb_chars=200),
                quantity=random.randint(0, 100),
                unit_price=round(random.uniform(10.0, 1000.0), 2)
            )
            products.append(product)
            self.stdout.write(f'Created product: {product.name}')

        # Create inventory records
        locations = ['Warehouse A', 'Warehouse B', 'Warehouse C', 'Storage 1', 'Storage 2']
        for product in products:
            Inventory.objects.create(
                product=product,
                quantity=product.quantity,
                location=random.choice(locations),
                last_updated=fake.date_time_between(start_date='-30d', end_date='now')
            )
            self.stdout.write(f'Created inventory for: {product.name}')

        # Create orders
        for _ in range(100):
            order = Order.objects.create(
                order_number=fake.unique.random_number(digits=8),
                supplier=random.choice(suppliers),
                status=random.choice(['pending', 'processing', 'completed', 'cancelled']),
                created_by=user,
                created_at=fake.date_time_between(start_date='-60d', end_date='now')
            )
            
            # Add 1-5 products to each order
            num_items = random.randint(1, 5)
            for _ in range(num_items):
                product = random.choice(products)
                quantity = random.randint(1, 5)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=product.unit_price
                )
            
            self.stdout.write(f'Created order: {order.order_number}')

        self.stdout.write(self.style.SUCCESS('Successfully generated fake data')) 