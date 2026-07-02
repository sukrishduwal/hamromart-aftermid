import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Category, Product
from .views import is_valid_phone_number


class PhoneNumberValidationTests(TestCase):
	def test_phone_number_rule(self):
		self.assertTrue(is_valid_phone_number('9812345678'))
		self.assertTrue(is_valid_phone_number('9712345678'))
		self.assertFalse(is_valid_phone_number('9912345678'))
		self.assertFalse(is_valid_phone_number('981234567'))
		self.assertFalse(is_valid_phone_number('98123456789'))

	def test_process_sale_rejects_invalid_phone(self):
		user = User.objects.create_user(username='cashier', password='pass12345')
		self.client.force_login(user)

		category = Category.objects.create(name='Shoes')
		product = Product.objects.create(
			name='Sneaker',
			sku='SKU-1',
			category=category,
			size='M',
			color='Black',
			cost_price=100,
			selling_price=150,
			quantity=10,
		)

		response = self.client.post(
			reverse('pos_checkout'),
			data=json.dumps({
				'phone': '9612345678',
				'name': 'Test Customer',
				'subtotal': 150,
				'tax': 7.5,
				'discount': 0,
				'total': 157.5,
				'cart': [{'id': product.id, 'qty': 1, 'price': 150}],
			}),
			content_type='application/json',
		)

		self.assertEqual(response.status_code, 400)
		self.assertIn('Phone number must be exactly 10 digits', response.json()['message'])
