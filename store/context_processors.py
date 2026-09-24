from .models import JewelryItem

def cart_items(request):
    cart = request.session.get('cart', {})
    items = []
    cart_count = sum(item['quantity'] for item in cart.values())
    subtotal = 0

    for product_id, item in cart.items():
        print("DEBUG ITEM:", item)   # 👈 add this

        price = float(item.get('price', 0))
        quantity = int(item.get('quantity', 0))

        total_price = price * quantity   # ✅ CORRECT
        subtotal += total_price
        
        items.append({
            'id': product_id,
            'product': {
                'id': product_id,
                'name': item.get('name'),
                'image': item.get('image')
            },
            'quantity': quantity,
            'total_price': total_price
        })

    return {
        'cart_items': items,
        'cart_count': sum(item['quantity'] for item in cart.values()),
        'cart_subtotal': subtotal
    }