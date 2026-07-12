from django.contrib import admin
from .models import Sale, SaleItem
from .models import DiscountScheme

class SaleAdmin(admin.ModelAdmin):
    change_list_template = 'admin/sale_changelist.html'

admin.site.register(Sale, SaleAdmin)
admin.site.register(SaleItem)
@admin.register(DiscountScheme)
class DiscountSchemeAdmin(admin.ModelAdmin):
    list_display = (
        'min_purchase',
        'step_amount',
        'step_discount',
        'max_discount',
        'is_active'
    )