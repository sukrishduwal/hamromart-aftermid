import json
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from products.models import Product
from customers.models import Customer
from .models import Sale, SaleItem

PHONE_NUMBER_RE = re.compile(r'^(97|98)\d{8}$')

def is_valid_phone_number(phone):
    phone = (phone or '').strip()
    return bool(PHONE_NUMBER_RE.fullmatch(phone))

@login_required
def pos_view(request):
    if not (
        request.user.is_superuser or
        request.user.groups.filter(name="Cashier").exists()
    ):
        raise PermissionDenied("You do not have permission to access the POS.")
    products = Product.objects.filter(quantity__gt=0)
    return render(request, 'pos/pos.html', {'products': products})

@login_required
def get_customer_history(request):
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
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            phone = (data.get('phone') or '').strip()
            if not is_valid_phone_number(phone):
                return JsonResponse(
                    {"status": "error", "message": "Phone number must be exactly 10 digits and start with 97 or 98."},
                    status=400,
                )
            
            customer = None
            if phone:
                customer, _ = Customer.objects.get_or_create(
                    phone=phone,
                    defaults={'name': data.get('name', 'Walk-in Customer')}
                )
            
            sale = Sale.objects.create(
                customer=customer,
                subtotal=data['subtotal'],
                discount=data['discount'],
                total=data['total']
            )

            for item in data['cart']:
                product = Product.objects.get(id=item['id'])
                SaleItem.objects.create(
                    sale=sale, 
                    product=product, 
                    quantity=item['qty'], 
                    price=item['price']
                )
                product.quantity -= int(item['qty'])
                product.save()

            return JsonResponse({"status": "success", "sale_id": sale.id, "bill_no": sale.bill_no})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

@login_required
def receipt_detail(request, pk):
    if not request.user.is_superuser:
        raise PermissionDenied("Only administrators are allowed to view receipt details.")
    sale = get_object_or_404(Sale, pk=pk)
    return render(request, 'receipt/receipt_detail.html', {'sale': sale})
