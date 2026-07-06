from django.contrib import admin
from .models import Sale, SaleItem

class SaleAdmin(admin.ModelAdmin):
    change_list_template = 'admin/sale_changelist.html'

admin.site.register(Sale, SaleAdmin)
admin.site.register(SaleItem)
