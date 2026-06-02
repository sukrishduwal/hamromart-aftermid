import json
from multiprocessing import context
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum , F, FloatField, ExpressionWrapper
from .models import Product, Category, Customer, Sale, SaleItem, Purchase
from datetime import timedelta
from django.utils import timezone
from django.db.models.functions import TruncDay
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .forms import ProductForm

# --- 1. DASHBOARD VIEW (Updated to use POS Sales) ---
@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('product_list')
    products = Product.objects.all()
    
    # 1. KPI Stats
    total_sales = Sale.objects.aggregate(Sum('total'))['total__sum'] or 0
    total_orders = Sale.objects.count()
    low_stock = products.filter(quantity__lt=10).count()

    # 2. Real Graph Logic (Ensure 7 days are always shown)
    today = timezone.now().date()
    # Create a list of the last 7 dates
    date_list = [today - timedelta(days=i) for i in range(6, -1, -1)]
    labels = [d.strftime('%b %d') for d in date_list]

    # Get actual sales data
    sales_data_query = Sale.objects.filter(timestamp__date__gte=date_list[0])\
        .annotate(day=TruncDay('timestamp'))\
        .values('day')\
        .annotate(daily_total=Sum('total'))
    
    # Map data to dates (put 0 where no sales exist)
    sales_map = {s['day'].date(): float(s['daily_total']) for s in sales_data_query}
    data = [sales_map.get(d, 0.0) for d in date_list]

    # 3. Real Top Categories logic
    total_qty = SaleItem.objects.aggregate(total=Sum('quantity'))['total'] or 1
    top_categories = SaleItem.objects.values(name=F('product__category__name'))\
        .annotate(qty=Sum('quantity'))\
        .annotate(percentage=ExpressionWrapper(F('qty') * 100.0 / total_qty, output_field=FloatField()))\
        .order_by('-qty')[:5]

    context = {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'low_stock': low_stock,
        'labels': labels,
        'data': data,
        'top_categories': top_categories,
    }
    return render(request, 'dashboard.html', context)
@login_required
# --- 2. INVENTORY MANAGEMENT ---
def product_list(request):
    products = Product.objects.all()
    return render(request, 'products.html', {'products': products})
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
    return render(request, 'product_form.html', {'form': form, 'title': 'Add Product'})

@login_required
def update_product(request, pk):
    product = get_object_or_404(Product, id=pk)
    # Store the original cost price to prevent regular users from accidentally changing/resetting it.
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
    return render(request, 'product_form.html', {'form': form, 'title': 'Edit Product'})
@login_required
# --- 3. NEW POS SYSTEM VIEWS ---
def pos_view(request):
    """Displays the POS interface"""
    products = Product.objects.filter(quantity__gt=0)
    return render(request, 'pos.html', {'products': products})
@login_required
def get_customer_history(request):
    """Retrieves customer name and recent sales via phone number"""
    phone = request.GET.get('phone')
    try:
        customer = Customer.objects.get(phone=phone)
        sales = Sale.objects.filter(customer=customer).order_by('-timestamp')[:3]
        history = [{"date": s.timestamp.strftime("%Y-%m-%d"), "total": float(s.total)} for s in sales]
        return JsonResponse({"status": "success", "name": customer.name, "history": history})
    except Customer.DoesNotExist:
        return JsonResponse({"status": "not_found"})

@login_required
def process_sale(request):
    """Handles the JSON data sent from the POS Cart to save the sale"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            
            # Create or identify customer
            customer = None
            if data.get('phone'):
                customer, _ = Customer.objects.get_or_create(
                    phone=data['phone'], 
                    defaults={'name': data.get('name', 'Walk-in Customer')}
                )
            
            # Create the Sale record
            sale = Sale.objects.create(
                customer=customer,
                subtotal=data['subtotal'],
                tax=data['tax'],
                discount=data['discount'],
                total=data['total']
            )

            # Save items and reduce stock
            for item in data['cart']:
                product = Product.objects.get(id=item['id'])
                SaleItem.objects.create(
                    sale=sale, 
                    product=product, 
                    quantity=item['qty'], 
                    price=item['price']
                )
                # Automated Inventory Update
                product.quantity -= int(item['qty'])
                product.save()

            return JsonResponse({"status": "success", "sale_id": sale.id,"bill_no": sale.bill_no})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

# Add this function at the bottom
@login_required
def sales_report(request):
    if not request.user.is_superuser:
        raise PermissionDenied("Only administrators are allowed to view sales reports.")
    total_revenue = Sale.objects.aggregate(Sum('total'))['total__sum'] or 0
    total_tax = Sale.objects.aggregate(Sum('tax'))['tax__sum'] or 0
    total_orders = Sale.objects.count()

    # Calculate Total Profit: (Selling Price - Cost Price) * Quantity sold
    all_sold_items = SaleItem.objects.all()
    total_profit = sum(item.quantity * (item.product.selling_price - item.product.cost_price) for item in all_sold_items)

    # Recent Sales with related customer and items
    recent_sales = Sale.objects.select_related('customer').prefetch_related('items__product').order_by('-timestamp')[:10]

    # Purchase history for products in recent sales
    product_ids = SaleItem.objects.filter(sale__in=recent_sales).values_list('product_id', flat=True).distinct()
    purchase_history = Purchase.objects.filter(product_id__in=product_ids).select_related('product').order_by('-purchase_date')
    top_products = SaleItem.objects.values('product__name').annotate(total_qty=Sum('quantity')).order_by('-total_qty')[:5]

    # Customer summary stats
    from django.db.models import Count
    customer_stats = Customer.objects.annotate(
        total_spent=Sum('sale__total'),
        order_count=Count('sale')
    )

    context = {
        'revenue': total_revenue,
        'tax': total_tax,
        'orders': total_orders,
        'profit': total_profit,
        'top_products': top_products,
        'recent_sales': recent_sales,
        'customer_stats': customer_stats,
        'purchase_history': purchase_history,
    }
    return render(request, 'sales_report.html', context)

@login_required
def receipt_detail(request, pk):
    if not request.user.is_superuser:
        raise PermissionDenied("Only administrators are allowed to view receipt details.")
    # Fetch the specific sale or show 404 if not found
    sale = get_object_or_404(Sale, pk=pk)
    # The template will use sale.items.all() because of the related_name in SaleItem
    return render(request, 'receipt_detail.html', {'sale': sale})



