from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='dashboard'),
    path('discount-settings/', views.discount_settings, name='discount_settings'),
]
