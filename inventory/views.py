from django.shortcuts import render, redirect, get_object_or_404

from .models import Product, Category, InventoryLog
from django.db.models import Sum, F

def admin_dashboard(request):
    products = Product.objects.all()
    # Logic for KPI cards
    total_value = sum(p.quantity * p.cost_price for p in products)
    low_stock = products.filter(quantity__lt=10).count()
    
    chart_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    chart_data = [5, 10, 7, 12, 8, 15, 20] # Placeholder data for sales trend
    context = {
        'total_inventory_value': total_value,
        'low_stock': low_stock,
        'products': products[:5], # Show only last 5 products
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }
    return render(request, 'dashboard.html', context)

def product_list(request):
    products = Product.objects.all()
    return render(request, 'products.html', {'products': products})

def delete_product(request, pk):
    # Use get_object_or_404 instead of .get() for safety
    product = get_object_or_404(Product, id=pk)
    product.delete()
    return redirect('product_list')