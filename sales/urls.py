from django.urls import path
from . import views

urlpatterns = [
    path('pos/', views.pos_view, name='pos_view'),
    path('pos/history/', views.get_customer_history, name='pos_history'),
    path('pos/checkout/', views.process_sale, name='pos_checkout'),
    path('receipt/<int:pk>/', views.receipt_detail, name='receipt_detail'),
]
