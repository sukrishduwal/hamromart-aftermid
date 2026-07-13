import json
from multiprocessing import context
from urllib import request
from django.shortcuts import render
from products.models import Product, Category



def product_list(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    stock_status = request.GET.get('stock', '')
    
    products = Product.objects.all().select_related('category')
    categories = Category.objects.all()
    
    if query:
        from django.db.models import Q
        products = products.filter(
            Q(name__icontains=query) |
            Q(sku__icontains=query) |
            Q(color__icontains=query) |
            Q(size__icontains=query)
        )
    
    if category_id:
        products = products.filter(category_id=category_id)
        
    if stock_status:
        if stock_status == 'low-stock':
            products = products.filter(quantity__lte=5)
        elif stock_status == 'in-stock':
            products = products.filter(quantity__gt=5)
            
    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'selected_category': int(category_id) if category_id.isdigit() else '',
        'selected_stock': stock_status,
    }
    return render(request, 'products.html', context)

def low_stock_items(request):
    """Display only low stock items"""
    low_stock_products = Product.objects.filter(quantity__lte=5).select_related('category').order_by('quantity')
    
    context = {
        'products': low_stock_products,
        'total_low_stock': low_stock_products.count(),
    }
    return render(request, 'inventory/low_stock.html', context)