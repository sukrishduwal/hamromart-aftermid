import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum
from .models import Product, Category, Customer, Sale, SaleItem

# --- 1. DASHBOARD VIEW (Updated to use POS Sales) ---
def admin_dashboard(request):
    products = Product.objects.all()
    
    # Real Inventory Stats
    total_value = sum(p.quantity * p.cost_price for p in products)
    low_stock = products.filter(quantity__lt=10).count()
    
    # POS Sales Stats (Calculated from our new Sale model)
    total_sales_amount = Sale.objects.aggregate(Sum('total'))['total__sum'] or 0
    total_orders_count = Sale.objects.count()
    
    # Chart Data
    chart_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    chart_data = [10, 25, 15, 45, 30, 60, 90] 

    context = {
        'total_inventory_value': total_value,
        'low_stock': low_stock,
        'total_sales': total_sales_amount,
        'total_orders': total_orders_count,
        'products': products[:5], 
        'labels': chart_labels,
        'data': chart_data,
    }
    return render(request, 'dashboard.html', context)

# --- 2. INVENTORY MANAGEMENT ---
def product_list(request):
    products = Product.objects.all()
    return render(request, 'products.html', {'products': products})

def delete_product(request, pk):
    product = get_object_or_404(Product, id=pk)
    product.delete()
    return redirect('product_list')

# --- 3. NEW POS SYSTEM VIEWS ---
def pos_view(request):
    """Displays the POS interface"""
    products = Product.objects.filter(quantity__gt=0)
    return render(request, 'pos.html', {'products': products})

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

            return JsonResponse({"status": "success", "sale_id": sale.id})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)