from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/update/<int:pk>/', views.update_product, name='update_product'),
    path('products/delete/<int:pk>/', views.delete_product, name='delete_product'),
    path('products/generate-sku/', views.generate_sku, name='generate_sku'),
    path('products/add-category-ajax/', views.add_category_ajax, name='add_category_ajax'),
    path('products/stock-levels/', views.stock_levels, name='stock_levels'),
]
