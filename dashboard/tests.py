from django.test import TestCase, Client
from django.contrib.auth.models import User
from products.models import Product, Category
from sales.models import Sale, SaleItem
from django.urls import reverse

class AdminDashboardTests(TestCase):
    def setUp(self):
        # Create a superuser
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password123'
        )
        self.client = Client()
        
        # Create Category and Product
        self.category = Category.objects.create(name='Test Category')
        self.product1 = Product.objects.create(
            name='Product A',
            sku='SKU001',
            category=self.category,
            cost_price=10.0,
            selling_price=15.0,
            quantity=100
        )
        self.product2 = Product.objects.create(
            name='Product B',
            sku='SKU002',
            category=self.category,
            cost_price=20.0,
            selling_price=30.0,
            quantity=100
        )
        
        # Create a sale and sale items
        self.sale = Sale.objects.create(
            subtotal=135.0,
            discount=0.0,
            total=135.0,
            payment_method='Cash',
            payment_status='Completed'
        )
        self.item1 = SaleItem.objects.create(
            sale=self.sale,
            product=self.product1,
            quantity=5,
            price=15.0
        )
        self.item2 = SaleItem.objects.create(
            sale=self.sale,
            product=self.product2,
            quantity=2,
            price=30.0
        )

    def test_admin_dashboard_requires_login(self):
        url = reverse('dashboard')
        response = self.client.get(url)
        self.assertRedirects(response, f'/login/?next={url}')

    def test_admin_dashboard_requires_superuser(self):
        # Create a regular user
        regular_user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='password123'
        )
        self.client.login(username='staff', password='password123')
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, reverse('product_list'))

    def test_admin_dashboard_context_contains_top_products(self):
        self.client.login(username='admin', password='password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        
        self.assertIn('top_products', response.context)
        self.assertIn('product_labels', response.context)
        self.assertIn('product_qty_data', response.context)
        
        # Check that product labels contain product names
        self.assertEqual(response.context['product_labels'], ['Product A', 'Product B'])
        self.assertEqual(response.context['product_qty_data'], [5, 2])
