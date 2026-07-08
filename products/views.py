import json
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Product, Category
from .forms import ProductForm


@login_required
def product_list(request):
    products = Product.objects.all().order_by('name')

    for product in products:
        product.display_stock = product.get_display_stock(request.user)

    return render(request, 'inventory/products.html', {
        'products': products,
    })


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
            prod = form.save(commit=False)
            prod.staff_quantity = min(25, prod.quantity)
            prod.save()

            # Create initial purchase record
            supplier = form.cleaned_data.get('supplier_name') or 'Initial Stock'
            price = form.cleaned_data.get('purchase_price') or prod.cost_price or 0
            from inventory.models import Purchase
            Purchase.objects.create(
                product=prod,
                supplier_name=supplier,
                purchase_price=price
            )
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
            # Recalculate staff_quantity whenever admin edits quantity
            prod.staff_quantity = min(25, prod.quantity)
            prod.save()

            # Record a new purchase if supplier details provided
            supplier = form.cleaned_data.get('supplier_name')
            price = form.cleaned_data.get('purchase_price')
            if supplier or price:
                from inventory.models import Purchase
                Purchase.objects.create(
                    product=prod,
                    supplier_name=supplier or 'Restock',
                    purchase_price=price or prod.cost_price or 0
                )
            return redirect('product_list')
    else:
        form = ProductForm(instance=product, user=request.user)

    purchases = product.purchase_set.all().order_by('-purchase_date')
    return render(request, 'inventory/product_form.html', {
        'form': form,
        'title': 'Edit Product',
        'purchases': purchases,
    })


@login_required
@require_POST
def add_category_ajax(request):
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        if not name:
            return JsonResponse({'status': 'error', 'message': 'Category name cannot be empty'}, status=400)
        if Category.objects.filter(name__iexact=name).exists():
            return JsonResponse({'status': 'error', 'message': 'A category with this name already exists'}, status=400)
        category = Category.objects.create(name=name)
        return JsonResponse({'status': 'success', 'id': category.id, 'name': category.name})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
def generate_sku(request):
    category_id = request.GET.get('category_id')
    if not category_id:
        return JsonResponse({'status': 'error', 'message': 'Category ID is required'}, status=400)
    try:
        category = Category.objects.get(id=category_id)
        clean_name = re.sub(r'[^a-zA-Z0-9]', '', category.name)
        prefix = clean_name[:3].upper() or 'PRD'
        sku_prefix = f"{prefix}-"
        max_num = 1000
        for prod in Product.objects.filter(sku__startswith=sku_prefix):
            parts = prod.sku.split('-')
            if len(parts) > 1:
                try:
                    num = int(parts[-1])
                    if num > max_num:
                        max_num = num
                except ValueError:
                    pass
        return JsonResponse({'status': 'success', 'sku': f"{prefix}-{max_num + 1}"})
    except Category.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Category not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
def stock_levels(request):
    """Real-time stock level API used by inventory page JS polling."""
    is_admin = request.user.is_superuser
    result = []
    for p in Product.objects.all().values('id', 'quantity', 'staff_quantity'):
        qty = p['quantity'] if is_admin else p['staff_quantity']
        result.append({
            'id': p['id'],
            'quantity': qty,
            'is_low': qty <= 5,
        })
    return JsonResponse({'products': result})
