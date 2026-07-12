from urllib import request
from customers.models import Customer 
from django.db import models
from products.models import Product
from django.contrib.auth.models import User

class Sale(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    timestamp = models.DateTimeField(
        auto_now_add=True
    )

    payment_method = models.CharField(
        max_length=20,
        default='Cash',
        choices=[
            ('Cash', 'Cash'),
            ('Khalti', 'Khalti')
        ]
    )

    payment_status = models.CharField(
        max_length=20,
        default='Completed',
        choices=[
            ('Pending', 'Pending'),
            ('Completed', 'Completed'),
            ('Cancelled', 'Cancelled')
        ]
    )
    cashier = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True
    )

    def __str__(self):
        return f"Sale {self.id}"

    @property
    def bill_no(self):
        return f"INV-{self.id + 1000}"

    def __str__(self):
        return self.bill_no

    class Meta:
        db_table = 'inventory_sale'

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'inventory_saleitem'
