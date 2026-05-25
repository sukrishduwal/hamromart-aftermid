from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='dashboard'),
    path('products/', views.product_list, name='product_list'),
]