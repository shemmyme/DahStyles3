
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404,HttpResponse
from userhome.models import *
from admin_side.models import *
from admin_side.models import *
from userhome.views import _cart_id
from userhome.views import *
from .models import *
from .forms import *
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
import datetime
from userhome.models import *


def checkout(request, total=0, quantity=0, cart_items=None):
    state= State.objects.all()
    city = City.objects.all()
    tax = 0
    grand_total = 0
    address = AddressDetails.objects.filter(user_id= request.user)
    
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True).order_by('id')
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True).order_by('id')
      
        for cart_item in cart_items:
            product_price = int(cart_item.product.price)
            total += product_price * int(cart_item.quantity)
            quantity += cart_item.quantity
            cart_item.price = product_price
            cart_item.save()
        
        tax = (2 * total) / 100
        grand_total = total + tax
        grand_total = format(grand_total, '.2f')
            
    except ObjectDoesNotExist:
        pass
     
    

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
        'address': address,
        'city' : city,
        'state' :state,
        
    }
    
    return render(request, 'checkout.html', context)

def confirmation(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(user=request.user)
        newAddress_id = request.POST.get('selected_addresses')
        total = cart.get_grand_total()
        # total = 'zz'
        grand_total = request.POST.get('grand_total')
        amountToBePaid = request.POST.get('amountToBePaid')
        couponCode = request.POST.get('couponCode')
        couponDiscount = request.POST.get('couponDiscount')

        if not newAddress_id:
            messages.error(request, 'Select An Address to Proceed to Checkout.')
            return redirect('checkout')
        else:
            address = AddressDetails.objects.get(id=newAddress_id)

    except ObjectDoesNotExist:
        pass
    
    val =  int(total * 100)
    print('val = ',val)
    
    try:
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY, settings.RAZORPAY_SECRET_KEY))
        payment = client.order.create({'amount': int(total)*100, 'currency': 'INR', 'payment_capture': 1})

        for cart_item in cart_items:
            cart_item.razor_pay_order_id = payment['id']
            cart_item.save()

        print('*****')
        print(payment)

        context = {
            'cart' : cart,
            'cart_items': cart_items,
            'addressSelected': address,
            'couponDiscount': couponDiscount,
            'couponCode': couponCode,
            'amountToBePaid': amountToBePaid,
            'payment': payment,
        }
        return render(request, 'confirm.html', context)
    except:
        return HttpResponse('Some payment informations you provided are not correct')


def calculateCartTotal(request):
   cart_items   = CartItem.objects.filter(user=request.user)
   if not cart_items:

       pass
   else:
      total = 0
      tax=0
      grand_total=0

      for cart_item in cart_items:
         total    += (cart_item.product.price * cart_item.quantity)
         tax = (5 * total) / 100
         grand_total = tax + total
   return total, tax, grand_total


def placeOrder(request):
   if request.method =='POST':
         if ('couponCode' in request.POST):
            instance = checkCoupon(request)

         cart_items   = CartItem.objects.filter(user=request.user)
         if not cart_items:
            return redirect('cart')
         
         newAddress_id = request.POST.get('addressSelected')
         address  = AddressDetails.objects.get(id = newAddress_id)
         newOrder =Order()
         newOrder.user=request.user
         newOrder.address = address
         yr = int(datetime.date.today().strftime('%Y'))
         dt = int(datetime.date.today().strftime('%d'))
         mt = int(datetime.date.today().strftime('%m'))
         d = datetime.date(yr,mt,dt)
         current_date = d.strftime("%Y%m%d")
         rand = str(random.randint(1111111,9999999))
         order_number = current_date + rand
         newPayment = Payment()
       
         newPayment.payment_id = request.POST.get('payment_id')

         payment_id  =order_number
         newPayment.payment_method = request.POST.get('payment_method')
         newPayment.customer = request.user
         newPayment.save()
         newOrder.payment = newPayment
         total, tax, grand_total = calculateCartTotal(request)
         newOrder.order_total = grand_total
         
         
         if(instance):
            if(instance.used == False):
                if float(grand_total) >= float(instance.coupon.min_value):
                    coupon_discount = ((float(grand_total) * float(instance.coupon.discount))/100)
                    amountToBePaid = float(grand_total) - coupon_discount
                    amountToBePaid = format(amountToBePaid, '.2f')
                    coupon_discount = format(coupon_discount, '.2f')
                    newOrder.order_discount = coupon_discount
                    newOrder.paid_amount = amountToBePaid
                    instance.used = True
                    newOrder.paid_amount = amountToBePaid
                    newOrder.tax = tax
                    newPayment.amount_paid = amountToBePaid
                    instance.save()
                else:
                    msg='This coupon is only applicable for orders more than ₹'+ str(instance.coupon.min_value)+ '\- only!'
            else:
                newOrder.paid_amount = grand_total
                newOrder.tax = tax
                newPayment.amount_paid = grand_total
                newOrder.discount=0
                msg = 'Coupon is not valid'
         else:
            newOrder.paid_amount = grand_total
            newOrder.tax = tax
            newPayment.amount_paid = grand_total
            msg = 'Coupon not Added'
         newPayment.save()
         newOrder.payment = newPayment
         order_number = order_number
         newOrder.order_number =order_number
         #to making order number unique
         while Order.objects.filter(order_number=order_number) is None:
            order_number = order_number
         newOrder.tax=tax
         newOrder.save()
         newPayment.order_id = newOrder.id
         newPayment.save()
         newOrderItems = CartItem.objects.filter(user=request.user)
         for item in newOrderItems:
            OrderProduct.objects.create(
                order = newOrder,
                customer=request.user,
                product=item.product,
                product_price=item.product.price,
                quantity=item.quantity
            )
            #TO DECRESE THE QUANTITY OF PRODUCT FROM CART
            orderproduct = Product.objects.filter(id=item.product_id).first()
            if(orderproduct.stock<=0):
               messages.warning(request,'Sorry, Product out of stock!')
               orderproduct.is_available = False
               orderproduct.save()
               item.delete()
               return redirect('viewcart')
            elif(orderproduct.stock < item.quantity):
               messages.success(request,  f"{orderproduct.stock} only left in cart.")
               return redirect('viewcart')
            else:
               orderproduct.stock -=  item.quantity
            orderproduct.save()
         if(instance):
            instance.order = newOrder
            instance.save()
        # TO CLEAR THE USER'S CART
         cart_item=CartItem.objects.filter(user=request.user)
         cart_item.delete()
         messages.success(request,'Order Placed Successfully')
         payMode =  request.POST.get('payment_method')
         print("===============================================================")
         print(payMode)
         if (payMode == "Paid by Razorpay" ):
            print(order_number,'--------------------order in place order---------------------')

            return JsonResponse ({'ordernumber':order_number,'status':"Your order has been placed successfully"})
         if (payMode == "COD" ):
            request.session['my_context'] = {'payment_id':payment_id}
            return redirect('order_complete', order_number )
   return redirect('checkout')


def checkCoupon(request):
   try:
      coupon_code = request.POST.get('couponCode')
      coupon = Coupon.objects.get(code = coupon_code)
      try:
         instance = UserCoupon.objects.get(user=request.user, coupon=coupon)
      except ObjectDoesNotExist:
         instance = None
         if(instance):
            pass
         else:
            instance = UserCoupon.objects.create(user = request.user ,coupon = coupon)
   except:
      instance = None
   return instance

def orderComplete(request,ordernumber) :

    order = Order.objects.get(user=request.user,order_number=ordernumber)
    orderitem = OrderProduct.objects.filter(customer=request.user,order=order)

    return render(request,'order_completed.html',locals())
 
def success(request):
    # try:
        print('success function is called')
        print(request.GET)
        razorpay_order_id = request.GET.get('razorpay_order_id')
        print("===========================================")
        print(razorpay_order_id)
        print('not this')
        cart = Cart.objects.get(razorpay_order_id=razorpay_order_id)
        print('cart obj error')

        # Payment details storing
        user = request.user
        transaction_id = request.GET.get('razorpay_payment_id')
        print('getiing cart total')
        cart_total = cart.get_cart_total()
        print('getting cart tax')
        # tax = cart.get_tax()
        
        
        print('gettingf g totalla')

        payment = Payment.objects.create(user=user, transaction_id=transaction_id, cart_total=cart_total)
        payment.save()
        
        print('before adderess')
        address_id = request.GET.get('address')
        print('address  : ' , address_id)
        delivery_address = AddressDetails.objects.get(user=user, id=address_id)
        
        # Creating the order in Order table
        order = Order.objects.create(order_id=razorpay_order_id, user=user, delivery_address=delivery_address, payment=payment)

        if cart.coupon:
            order.coupon = cart.coupon
            order.save()

        # Storing ordered products in OrderItem table
        order_items = CartItem.objects.filter(cart=cart)
        for item in order_items:
            item.product.stock -= item.quantity
        
            item.product.save()
        
            ordered_item = OrderProduct.objects.create(user=user,order=order, product=item.product, item_price=item.get_product_price(), quantity=item.quantity, item_total=cart.get_cart_total())
        

            ordered_item.save()
            
       

        # Deleting the cart once it is ordered/paid
        cart.is_active = False
        cart.delete()

        return render(request, 'success.html', {'order_id': razorpay_order_id})
    
def razorPayCheck(request):
   total=0
#    coupon_discount =0
   amountToBePaid = 0
   current_user=request.user
   cart_items=CartItem.objects.filter(user_id=current_user.id)
   if cart_items:
      for cart_item in cart_items:
         total+=(cart_item.product.price*cart_item.quantity)
      tax = (5 * total) / 100
      grand_total=int(total+tax)
      grand_total = round(grand_total,2)
      amountToBePaid = grand_total
      print()
      return JsonResponse({
         'grand_total' : grand_total,
        #  'coupon': coupon,
        #  'coupon_discount':coupon_discount,
         'amountToBePaid':amountToBePaid
      })
   else:
      return redirect('shop',0)

import os
from razorpay.errors import BadRequestError,ServerError


def cancelOrder(request):
    if request.method == 'POST':
            id = request.POST.get('id')

    client = razorpay.Client(auth=(os.getenv("KEY_ID"), os.getenv("SECRET_KEY")))
    try:
        order = Order.objects.get(id=id,user=request.user)
    except Order.DoesNotExist:
        # Handle the case where the order does not exist
        order = None
    
    if order is None:
        # Render an error message if the order does not exist
        messages.warning(request,'The order you are trying to cancel does not exist.')
        return redirect(order)
    
    payment=order.payment
    msg=''
    
    if (payment.payment_method == 'Paid by Razorpay'):
        payment_id = payment.payment_id
        amount = payment.amount_paid
        amount= amount*100
        try :
            # captured_amount = client.payment.capture(payment_id,amount)
            pass
        except BadRequestError as e:
            # Handle a BadRequestError from Razorpay
            captured_amount = None
            messages.warning(request,'The payment has not been captured.Please try again later. If the issue continues, CONTACT THE SUPPORT TEAM!')
            return redirect(order)
        #   except ServerError as e:
              # Handle a ServerError from Razorpay
        #   captured_amount = None
            # msg = "Server error occurred while capturing the payment."

        # if captured_amount is not None and captured_amount['status'] == 'captured' :
        #     refund_data = {
        #         "payment_id": payment_id,
        #         "amount": amount,  # amount to be refunded in paise
        #         "currency": "INR",
        #     }
            
        #     refund = client.payment.refund(payment_id, refund_data)
            #  except BadRequestError as e:
            #      # Handle a BadRequestError from Razorpay
            #      refund = None
            #      msg = "Bad request error occurred while processing the refund."
            #  except ServerError as e:
            #      # Handle a ServerError from Razorpay
            #      refund = None
            #      msg = "Server error occurred while processing the refund."
            # print(refund)
            
            if refund is not None:
                current_user=request.user
                order.refund_completed = True
                order.status = 'Cancelled'
                payment = order.payment
                payment.refund_id = refund['id']
                payment.save()
                order.save()
                messages.success(request,'Your order has been successfully cancelled and amount has been refunded!')
                mess=f'Hai\t{current_user.username},\nYour order has been canceled, Money will be refunded with in 1 hour\nThanks!'
                try:
                    send_mail(
                            "Order Cancelled",
                            mess,
                            settings.EMAIL_HOST_USER,
                            [current_user.email],
                            fail_silently = False
                        )
                except Exception as e:
                    # Handle an exception while sending email
                    msg += "\nError occurred while sending an email notification."
            else :
                messages.warning(request,'Your order is not cancelled because the refund could not be completed now. Please try again later. If the issue continues, CONTACT THE SUPPORT TEAM!')
                pass
        else :
            if(payment.paid):
                order.refund_completed = True
                order.status = 'Cancelled'
                messages.success(request,'YOUR ORDER HAS BEEN SUCCESSFULLY CANCELLED!')
                order.save()
            else:
                order.status = 'Cancelled'
                order.save()
                messages.success(request,'Your payment has not been recieved yet. But the order has been cancelled.!')
    else :
        order.status = 'Cancelled'
        messages.success(request,'YOUR ORDER HAS BEEN SUCCESSFULLY CANCELLED!')
        order.save()
    return redirect('orderbook')