from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=100, default="Walk-in Customer")
    phone = models.CharField(max_length=15, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.phone})"

    class Meta:
        db_table = 'inventory_customer'
