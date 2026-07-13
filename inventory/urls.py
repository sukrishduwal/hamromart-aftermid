from django.urls import path
from . import views

urlpatterns = [
    path('low-stock/', views.low_stock_items, name='low_stock_items'),
    path('export-purchase-excel/', views.export_purchase_excel, name='export_purchase_excel'),
]