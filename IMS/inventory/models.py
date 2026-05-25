from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')

class Variation(models.Model):
    # Clothing specific variants
    SIZE_CHOICES = [('S', 'Small'), ('M', 'Medium'), ('L', 'Large'), ('XL', 'Extra Large')]
    product = models.ForeignKey(Product, related_name='variations', on_delete=models.CASCADE)
    size = models.CharField(max_length=2, choices=SIZE_CHOICES)
    color = models.CharField(max_length=50)
    stock = models.PositiveIntegerField(default=0)  # Inventory management
    price_modifier = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class Order(models.Model):
    STATUS = [('Pending', 'Pending'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered')]
    customer_name = models.CharField(max_length=100)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    variation = models.ForeignKey(Variation, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()