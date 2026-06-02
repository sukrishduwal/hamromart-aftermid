from django.contrib import admin
from .models import Category, Customer, Product, Sale, SaleItem

# Register models
admin.site.register(Category)
admin.site.register(Customer)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # This makes the product list look professional with columns
    list_display = ('name', 'sku', 'category', 'quantity', 'selling_price')
    search_fields = ('name', 'sku')
    list_filter = ('category',)

class SaleAdmin(admin.ModelAdmin):
    # Use custom change list template to add a button linking to sales report
    change_list_template = 'admin/sale_changelist.html'

admin.site.register(Sale, SaleAdmin)
admin.site.register(SaleItem)