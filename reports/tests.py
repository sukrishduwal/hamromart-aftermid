from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from products.models import Product, Category
from sales.models import Sale, SaleItem
from customers.models import Customer
from django.core.exceptions import PermissionDenied

class SalesReportTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password123'
        )
        self.regular_user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='password123'
        )
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            sku='SKU999',
            category=self.category,
            cost_price=50.0,
            selling_price=100.0,
            quantity=100
        )
        self.customer = Customer.objects.create(
            name='Test Customer',
            phone='9876543210'
        )
        self.sale = Sale.objects.create(
            customer=self.customer,
            subtotal=100.0,
            discount=0.0,
            total=100.0,
            payment_method='Cash',
            payment_status='Completed'
        )
        self.item = SaleItem.objects.create(
            sale=self.sale,
            product=self.product,
            quantity=2,
            price=100.0
        )

    def test_sales_report_requires_login(self):
        url = reverse('sales_report')
        response = self.client.get(url)
        self.assertRedirects(response, f'/login/?next={url}')

    def test_sales_report_requires_superuser(self):
        self.client.login(username='staff', password='password123')
        response = self.client.get(reverse('sales_report'))
        # The view raises PermissionDenied, which is translated to 433/403 forbidden
        self.assertEqual(response.status_code, 403)

    def test_sales_report_as_superuser(self):
        self.client.login(username='admin', password='password123')
        response = self.client.get(reverse('sales_report'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('revenue', response.context)
        self.assertIn('profit', response.context)
        self.assertIn('orders', response.context)
        self.assertEqual(float(response.context['revenue']), 100.0)
        # Profit should be quantity (2) * (selling - cost) (100 - 50) = 100
        self.assertEqual(float(response.context['profit']), 100.0)
        self.assertEqual(response.context['orders'], 1)
