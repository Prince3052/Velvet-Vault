from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from store.models import JewelryItem
from .models import Order
import json
from django.http import JsonResponse
# Create your views here.

@login_required(login_url='login')
def checkout_page(request):
    cart = request.session.get('cart', {})

    items = []
    subtotal = 0

    for product_id, item in cart.items():
        price = float(item['price'])
        quantity = int(item['quantity'])
        total = price * quantity
        subtotal += total

        items.append({
            'id': product_id,
            'name': item['name'],
            'price': price,
            'quantity': quantity,
            'total': total,
            'image': item['image']
        })

    return render(request, 'checkout/checkout.html', {
        'cart_items': items,
        'cart_total': subtotal
    })
    

def payment_method(request):
    if request.method == "POST":
        request.session['checkout_data'] = {
            'email': request.POST.get('email'),
            'name': request.POST.get('name'),
            'phone': request.POST.get('phone'),
            'address': request.POST.get('address'),
        }

        return redirect('payment_options')

    return redirect('checkout') 

def payment_options(request):
    return render(request, 'checkout/payment_method.html', {
        "razorpay_key": 'rzp_test_SZ57CqweGXDQvu',
        "page_title": "Payment"
    })

def place_order(request):
    if request.method == "POST":
        data = json.loads(request.body)
        cart = request.session.get('cart', {})

        orders = []

        for product_id, item in cart.items():
            product = JewelryItem.objects.get(id=product_id)

            order = Order.objects.create(
                user=request.user,
                product=product,
                amount=item['price'],
                payment_method=data['payment_method'],
                is_paid=False
            )
            orders.append(order.pk)

        # clear cart
        request.session['cart'] = {}

        return JsonResponse({
            "status": "success",
            "order_ids": orders,
            "error": "Invalid request"
        }, status=400)