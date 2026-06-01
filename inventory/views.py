import json
from multiprocessing import context
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum , F, FloatField, ExpressionWrapper
from .models import Product, Category, Customer, Sale, SaleItem
from datetime import timedelta
from django.utils import timezone
from django.db.models.functions import TruncDay
from django.contrib.auth.decorators import login_required

# --- 1. DASHBOARD VIEW (Updated to use POS Sales) ---
@login_required
def admin_dashboard(request):
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
    product = get_object_or_404(Product, id=pk)
    product.delete()
    return redirect('product_list')
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
    total_revenue = Sale.objects.aggregate(Sum('total'))['total__sum'] or 0
    total_tax = Sale.objects.aggregate(Sum('tax'))['tax__sum'] or 0
    total_orders = Sale.objects.count()

    # Calculate Total Profit: (Selling Price - Cost Price) * Quantity sold
    all_sold_items = SaleItem.objects.all()
    total_profit = sum(item.quantity * (item.product.selling_price - item.product.cost_price) for item in all_sold_items)

    # Top 5 Selling Products
    top_products = SaleItem.objects.values('product__name').annotate(
        total_qty=Sum('quantity')
    ).order_by('-total_qty')[:5]

    # Recent Sales
    recent_sales = Sale.objects.all().order_by('-timestamp')[:10]

    context = {
        'revenue': total_revenue,
        'tax': total_tax,
        'orders': total_orders,
        'profit': total_profit,
        'top_products': top_products,
        'recent_sales': recent_sales,
    }
    return render(request, 'sales_report.html', context)

@login_required
def receipt_detail(request, pk):
    # Fetch the specific sale or show 404 if not found
    sale = get_object_or_404(Sale, pk=pk)
    # The template will use sale.items.all() because of the related_name in SaleItem
    return render(request, 'receipt_detail.html', {'sale': sale})



