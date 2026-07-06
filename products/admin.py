from django.contrib import admin
from .models import Category, Product

admin.site.register(Category)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'quantity', 'selling_price')
    search_fields = ('name', 'sku')
    list_filter = ('category',)
