from django.shortcuts import render, redirect
from .models import JewelryItem, Cart, CartItem
from django.shortcuts import redirect, get_object_or_404
from .models import *
from django.http import JsonResponse
from django.core.mail import send_mail
from .forms import ContactForm
from django.conf import settings
from django.http import JsonResponse
from django.http import request
from django.contrib.auth.decorators import login_required
import json
import razorpay
from payments.models import Payment
# Create your views here.

def home_page(request):
    collections = Collection.objects.all()
    products = JewelryItem.objects.all()
    cart = request.session.get('cart', {})
    cart_items = []
    for product_id, item in cart.items():
        cart_items.append({
            'id': product_id,
            'product': {
                'id': product_id,
                'name': item['name'],
                'image': item['image']
            },
            'quantity': item['quantity'],
            'total_price': float(item['price']) * item['quantity']
        })
    return render(request, 'store/index.html', {'products': products, 'collections': collections, 'page_title': 'Home', 'cart_items': cart_items})

def product_detail(request, slug): 
    product = get_object_or_404(JewelryItem, slug=slug)
    collections = Collection.objects.all()
    related_products = JewelryItem.objects.filter(
        category=product.category
    ).exclude(slug=slug)[:4]
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    amount = int(float(product.price) * 100)
    order = client.order.create({  # type: ignore
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })
    # Save payment record
    Payment.objects.create(
        product=product,
        amount=amount,
        razorpay_order_id=order['id']
    )
    return render(request, 'store/product_detail.html', { 
        'product': product,
        'page_title': 'Product Page',
        'related_products': related_products,
        'collections': collections,
        'order': order,  # ✅ IMPORTANT
        'razorpay_key': settings.RAZORPAY_KEY_ID  # ✅ IMPORTANT
    })

#search products
def search_products(request):
    query = request.GET.get('q', '')

    products = JewelryItem.objects.filter(
        name__icontains=query,
        is_active=True
    )[:10]

    data = [
        {
            "slug": p.slug,
            "name": p.name,
            "price": str(p.price),
            "image": p.image.url if p.image else "",
        }
        for p in products
    ]

    return JsonResponse(data, safe=False)

#Add to cart
def add_to_cart(request, pk):
    product = JewelryItem.objects.get(pk=pk)
    print("SESSION CART:", request.session.get('cart'))
    cart = request.session.get('cart', {})

    product_id = str(product.pk)

    if product_id in cart:
        cart[product_id]['quantity'] += 1
    else:
        cart[product_id] = {
            'name': product.name,
            'price': float(product.price) if product.price else 0,
            'image': product.image.url if product.image else '',
            'quantity': 1
        }

    # ✅ SAVE SESSION (VERY IMPORTANT)
    request.session['cart'] = cart
    request.session.modified = True

    cart_count = sum(item['quantity'] for item in cart.values())
    cart_subtotal = sum(
        float(item['price']) * int(item['quantity'])
        for item in cart.values()
    )
    return JsonResponse({
        'status': 'success',
        'product_id': product.pk,
        'name': product.name,
        'price': product.price,
        'image': product.image.url if product.image else '',
        'quantity': cart[product_id]['quantity'],
        'cart_count': cart_count,
        'cart_subtotal': cart_subtotal
    })
#Cart Drawer
def cart_drawer(request):
    cart = request.session.get("cart", {})

    print("SESSION CART:", cart)  # 🔥 ADD THIS

    cart_items = []
    cart_total = 0

    for product_id, quantity in cart.items():
        product = JewelryItem.objects.get(id=product_id)

        total = product.price * quantity
        cart_total += total

        cart_items.append({
            "name": product.name,
            "price": product.price,
            "image": product.image.url if product.image else "",
            "quantity": quantity,
            "total": total
        })

    return render(request, "cart/cart_drawer.html", {
        "cart_items": cart_items,
        "cart_total": cart_total
    })

#Cart Items
def buy_now(request, pk):
    product = get_object_or_404(JewelryItem, pk=pk)
    return redirect("checkout")


#Update Cart Products
def update_cart(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        action = request.POST.get("action")

        cart = request.session.get("cart", {})

        quantity = 0
        item_total = 0

        if product_id in cart:

            if action == "increase":
                cart[product_id]["quantity"] += 1

            elif action == "decrease":
                cart[product_id]["quantity"] -= 1

                if cart[product_id]["quantity"] <= 0:
                    del cart[product_id]

                    request.session["cart"] = cart
                    request.session.modified = True

                    subtotal = sum(
                        float(item["price"]) * int(item["quantity"])
                        for item in cart.values()
                    )

                    return JsonResponse({
                        "removed": True,
                        "cart_count": sum(item["quantity"] for item in cart.values()),
                        "cart_subtotal": subtotal
                    })

            # ✅ NOW SAFE
            quantity = cart[product_id]["quantity"]
            price = float(cart[product_id]["price"])
            item_total = price * quantity

        # save session
        request.session["cart"] = cart
        request.session.modified = True

        subtotal = sum(
            float(item["price"]) * int(item["quantity"])
            for item in cart.values()
        )

        return JsonResponse({
            "removed": False,
            "quantity": quantity,
            "item_total": item_total,
            "cart_count": sum(item["quantity"] for item in cart.values()),
            "cart_subtotal": subtotal
        })

    return JsonResponse({"status": "error"})

#Remove Cart
def remove_from_cart(request):
    if request.method == "POST":
        product_id = request.POST.get('product_id')
        cart = request.session.get('cart', {})
        if product_id in cart:
            del cart[product_id]
        request.session['cart'] = cart
        request.session.modified = True
        cart_count = sum(item['quantity'] for item in cart.values())
        return JsonResponse({
            'status': 'success',
            'cart_count': cart_count
        })
    return JsonResponse({'status': 'error'})

@login_required(login_url='login')
def checkout(request, slug):
    product = get_object_or_404(JewelryItem, slug=slug)
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    amount = int(float(product.price) * 100)
    order = client.order.create({  # type: ignore
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })
    # Save payment record
    Payment.objects.create(
        product=product,
        amount=amount,
        razorpay_order_id=order['id']
    )
    return render(request, "checkout.html")

#About Us Page
def about_page(request):
    collection = Collection.objects.get(id=1)
    collections = Collection.objects.all()
    products = collection.products.all()
    members = TeamMember.objects.all()
    return render(request, 'store/about.html', { 
        'collection': collection, 
        'members': members, 
        'products': products,
        'page_title': 'About Us',
        'collections': collections
        })


#collection page
def collection_page(request, id):
    collection = Collection.objects.get(id=id)
    products = collection.products.all()
    collections = Collection.objects.all()

    return render(request, 'store/collection.html', {    
        'collection': collection, 
        'products': products,
        'page_title': 'Collection',
        'collections': collections
    })

#blogs
def blog_list(request):
    blogs = Blog.objects.filter(is_published=True).order_by('-created_at')
    collections = Collection.objects.all()
    return render(request, 'store/blog_list.html', {'blogs': blogs, 'page_title': 'Bolgs', 'collections': collections})

def blog_detail(request, slug):
    blog = Blog.objects.get(slug=slug, is_published=True)
    collections = Collection.objects.all()
    return render(request, 'store/blog_detail.html', {'blog': blog, 'page_title': 'Blog', 'collections': collections})

#faq page
def faq_page(request):
    collections = Collection.objects.all()
    return render(request, 'store/faq.html', {'page_title': 'FAQ', 'collections': collections})


def success_page(request):
    collections = Collection.objects.all()
    return render(request, 'store/success.html', {'page_title': 'Success', 'collections': collections})

#Contact Page
def contact_page(request):
    collections = Collection.objects.all()
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            comment = form.cleaned_data['comment']
            subject = f"New Contact Form Submission from {name}"
            message = f"Name: {name}\nEmail: {email}\n\nComment:\n{comment}"
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [settings.EMAIL_HOST_USER])
            return redirect('success_page')  # redirect to a success page
    else:
        form = ContactForm()

    return render(request, 'store/contact.html', {'form': form, 'page_title': 'Contact', 'collections': collections})

