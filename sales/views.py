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

STAFF_POOL_MAX = 25   # max units visible to staff at once
STAFF_LOW_THRESHOLD = 5  # trigger auto-restore when staff pool hits this


def is_valid_phone_number(phone):
    phone = (phone or '').strip()
    return bool(PHONE_NUMBER_RE.fullmatch(phone))


@login_required
def pos_view(request):
    # Both admin and staff can access POS
    if not ( request.user.groups.filter(name='Cashier').exists()):
        raise PermissionDenied("You do not have permission to access the POS.")
    # Staff only sees products with remaining staff_quantity
    is_admin = request.user.is_superuser
    if is_admin:
        products = Product.objects.filter(quantity__gt=0).order_by('name')
    else:
        products = Product.objects.filter(staff_quantity__gt=0).order_by('name')
    return render(request, 'pos/pos.html', {
        'products': products,
        'is_admin': is_admin,
        'staff_low_threshold': STAFF_LOW_THRESHOLD,
    })


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
                discount=data.get('discount', 0),
                total=data['total'],
            )

            is_admin = request.user.is_superuser

            for item in data['cart']:
                product = Product.objects.get(id=item['id'])
                qty_sold = int(item['qty'])

                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=qty_sold,
                    price=item['price'],
                )

                # Deduct from master stock (always)
                product.quantity = max(0, product.quantity - qty_sold)

                if is_admin:
                    # Admin sells from master — also bring staff_quantity in sync
                    product.staff_quantity = min(STAFF_POOL_MAX, product.quantity)
                else:
                    # Staff sells from their pool
                    product.staff_quantity = max(0, product.staff_quantity - qty_sold)

                product.save()

                # Auto-restore staff pool if running low and master stock available
                if (product.staff_quantity <= STAFF_LOW_THRESHOLD and
                        product.quantity > product.staff_quantity):
                    restore_to = min(STAFF_POOL_MAX, product.quantity)
                    product.staff_quantity = restore_to
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
