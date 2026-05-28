from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='dashboard'),
    path('products/', views.product_list, name='product_list'),
    path('products/delete/<int:pk>/', views.delete_product, name='delete_product'),
    path('pos/', views.pos_view, name='pos'),
    path('pos/', views.pos_view, name='pos'),
    path('pos/history/', views.get_customer_history, name='pos_history'),
    path('pos/checkout/', views.process_sale, name='pos_checkout'),
]