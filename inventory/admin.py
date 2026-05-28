from django.contrib import admin
from .models import Category, Customer, Product, InventoryLog, Sale, SaleItem

# This tells Django to show these tables in the admin area
admin.site.register(Category)
admin.site.register(InventoryLog)
admin.site.register(Customer)
admin.site.register(Sale)
admin.site.register(SaleItem)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # This makes the product list look professional with columns
    list_display = ('name', 'sku', 'category', 'quantity', 'selling_price')
    search_fields = ('name', 'sku')
    list_filter = ('category',)