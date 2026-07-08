from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self): 
        return self.name

    class Meta:
        db_table = 'inventory_category'

class Product(models.Model):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    color = models.CharField(max_length=50, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    staff_quantity = models.PositiveIntegerField(default=0, help_text="Staff working pool (auto-capped at 25)")
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    admin_stock = models.PositiveIntegerField(default=0)
    staff_stock = models.PositiveIntegerField(default=25)

    def get_display_stock(self, user):
        if user.is_superuser:
            return self.quantity
        return self.staff_quantity
    
    @property
    def profit_per_unit(self):
        return self.selling_price - self.cost_price
    
    @property
    def latest_supplier(self):
        latest = self.purchase_set.order_by('-purchase_date').first()
        return latest.supplier_name if latest else 'N/A'

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'inventory_product'
