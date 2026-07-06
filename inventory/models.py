from django.db import models
from django.utils import timezone
from products.models import Product

class Purchase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    supplier_name = models.CharField(max_length=100)
    purchase_date = models.DateTimeField(default=timezone.now)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.supplier_name} - {self.product.name}"

    class Meta:
        db_table = 'inventory_purchase'