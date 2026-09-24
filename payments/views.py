import razorpay
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from .models import Payment
from store.models import JewelryItem
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def create_order(request, product_id):
    product = JewelryItem.objects.get(id=product_id)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    amount = int(product.price * 100)

    order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })

    payment = Payment.objects.create(
        user=request.user,   # ✅ IMPORTANT
        product=product,
        amount=amount,
        razorpay_order_id=order['id']
    )

    return JsonResponse({
        "order_id": order["id"],
        "amount": amount,
        "key": settings.RAZORPAY_KEY_ID
    })


#Verify Payment
def verify_payment(request):
    if request.method == "POST":
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        data = request.POST

        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': data['razorpay_order_id'],
                'razorpay_payment_id': data['razorpay_payment_id'],
                'razorpay_signature': data['razorpay_signature']
            })

            payment = Payment.objects.get(razorpay_order_id=data['razorpay_order_id'])
            payment.razorpay_payment_id = data['razorpay_payment_id']
            payment.razorpay_signature = data['razorpay_signature']
            payment.user = request.user   # optional safety
            payment.status = "success"
            payment.save()

            return JsonResponse({"status": "success"})

        except Exception as e:
            print(e)
            return JsonResponse({"status": "failed"})
        
@login_required(login_url='login')
def my_orders(request):
    orders = Payment.objects.filter(user=request.user).order_by('-created_at')

    return render(request, "payments/my_orders.html", {
        "orders": orders
    })