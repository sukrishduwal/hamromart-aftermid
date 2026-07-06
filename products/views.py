from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import Product, Category
from .forms import ProductForm

@login_required
def product_list(request):
    products = Product.objects.all()
    return render(request, 'inventory/products.html', {'products': products})

@login_required
def delete_product(request, pk):
    if not request.user.is_superuser:
        raise PermissionDenied("Only administrators are allowed to delete products.")
    product = get_object_or_404(Product, id=pk)
    product.delete()
    return redirect('product_list')

@login_required
def add_product(request):
    if not request.user.is_superuser:
        raise PermissionDenied("Only administrators are allowed to add products.")
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(user=request.user)
    return render(request, 'inventory/product_form.html', {'form': form, 'title': 'Add Product'})

@login_required
def update_product(request, pk):
    product = get_object_or_404(Product, id=pk)
    original_cost_price = product.cost_price
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product, user=request.user)
        if form.is_valid():
            prod = form.save(commit=False)
            if not request.user.is_superuser:
                prod.cost_price = original_cost_price
            prod.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product, user=request.user)
    return render(request, 'inventory/product_form.html', {'form': form, 'title': 'Edit Product'})
