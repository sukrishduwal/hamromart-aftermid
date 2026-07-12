from django.shortcuts import render, redirect
from django.db.models import Sum, F, FloatField, ExpressionWrapper
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models.functions import TruncDay
from datetime import timedelta
from products.models import Product
from sales.models import Sale, SaleItem, DiscountScheme

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
    return render(request, 'dashboard/dashboard.html', context)
def discount_settings(request):
    scheme, created = DiscountScheme.objects.get_or_create(id=1)

    if request.method == "POST":
        scheme.min_purchase = request.POST.get("min_purchase")
        scheme.step_amount = request.POST.get("step_amount")
        scheme.step_discount = request.POST.get("step_discount")
        scheme.max_discount = request.POST.get("max_discount")
        scheme.save()

        return redirect("discount_settings")

    return render(request, "dashboard/discount_settings.html", {
        "scheme": scheme
    })