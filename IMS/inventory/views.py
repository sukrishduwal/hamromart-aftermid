from django.shortcuts import render
from django.db.models import Sum
from .models import Order, Product, Variation

def admin_dashboard(request):
    # Dummy data for now so it doesn't crash if database is empty
    context = {
        'total_sales': 0,
        'total_orders': 0,
        'low_stock': 0,
        'labels': ["Mon", "Tue", "Wed"],
        'data': [10, 20, 30],
    }
    return render(request, 'dashboard.html', context)

def product_list(request):
    products = Product.objects.all()
    return render(request, 'products.html', {'products': products})