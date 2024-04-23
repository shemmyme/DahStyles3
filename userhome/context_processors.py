from .models import Cart, CartItem
from .views import _cart_id


from django.shortcuts import render
from .models import Cart, CartItem

def counter(request):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart)
        print(cart)
        print(cart_items)
        cart_count = 0
        for cart_item in cart_items:
            cart_count += cart_item.quantity
    except Cart.DoesNotExist:
        cart_count = 0

    return {'count_cart': cart_count}
