from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Sum, Count
from sales.models import Sale, SaleItem
from customers.models import Customer
from inventory.models import Purchase

@login_required
def sales_report(request):
    if not request.user.is_superuser:
        raise PermissionDenied("Only administrators are allowed to view sales reports.")
    total_revenue = Sale.objects.aggregate(Sum('total'))['total__sum'] or 0
    total_orders = Sale.objects.count()

    all_sold_items = SaleItem.objects.all()
    total_profit = sum(item.quantity * (item.product.selling_price - item.product.cost_price) for item in all_sold_items)

    recent_sales = Sale.objects.select_related('customer').prefetch_related('items__product').order_by('-timestamp')[:10]
    
    product_ids = SaleItem.objects.filter(sale__in=recent_sales).values_list('product_id', flat=True).distinct()
    purchase_history = Purchase.objects.filter(product_id__in=product_ids).select_related('product').order_by('-purchase_date')
    top_products = SaleItem.objects.values('product__name').annotate(total_qty=Sum('quantity')).order_by('-total_qty')[:5]

    customer_stats = Customer.objects.annotate(
        total_spent=Sum('sale__total'),
        order_count=Count('sale')
    ).order_by('-total_spent')[:10]

    purchase_history = Purchase.objects.filter(product_id__in=product_ids).select_related('product').order_by('-purchase_date')[:10]
    
    context = {
        'revenue': total_revenue,
        'orders': total_orders,
        'profit': total_profit,
        'top_products': top_products,
        'recent_sales': recent_sales,
        'customer_stats': customer_stats,
        'purchase_history': purchase_history,
    }
    return render(request, 'reports/sales_report.html', context)

def checkout(request):
    if request.method == 'POST':
        # window.print()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})