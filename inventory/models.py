from django.db import models
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self): return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True) # Barcode support
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    size = models.CharField(max_length=10, choices=[('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL')])
    color = models.CharField(max_length=50, null=False, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    @property
    def profit_per_unit(self):
        return self.selling_price - self.cost_price
    
    
    def __str__(self):
        return f"{self.name} - {self.size}"

    def get_absolute_url(self):
        return reverse('product_list')

# HISTORY LOG SYSTEM
class InventoryLog(models.Model):
    LOG_TYPES = [('ADD', 'Stock Added'), ('SUB', 'Stock Reduced'), ('SALE', 'Sale')]
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    change_type = models.CharField(max_length=10, choices=LOG_TYPES)
    quantity = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    note = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.product.name} | {self.change_type} | {self.quantity}"