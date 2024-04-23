from django.shortcuts import render,redirect,get_object_or_404,HttpResponse
from admin_side.models import *
from .models import *
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import random
from .forms import *
from django.core.exceptions import ObjectDoesNotExist
import datetime
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from admin_side.views import *
from userhome.views import *
from .forms import *
from .models import *
from order.models import *
from django.core.mail import send_mail,EmailMessage
import random
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
import razorpay


def error_404_view(request,exception):
    return render(request,'404.html')

def login(request):
    if request.method == 'POST':
        username=request.POST['email']
        password=request.POST['password']
        user =auth.authenticate(username=username,password=password) 
        print(user)
        if user is not None: 
            auth.login(request,user)         
            return redirect(home)
        else:
            messages.success(request, 'Invalid login credentials')
            return redirect(login)
    return render(request,'login.html')


    #  if request.method == 'POST':
    #     email = request.POST['email']
    #     password = request.POST['password']
    #     user = auth.authenticate( email=email, password=password)
    #     if user is not None:
    #         login(request, user)
    #         return redirect(home)
        


def register(request):
    usr = None
    #Register Form
    if request.method=='POST':
        get_otp=request.POST.get('otp')
        # OTP Verification
        if get_otp:
            get_usr=request.POST.get('usr')
            usr=Customer.objects.get(username=get_usr)
            if int(get_otp)==UserOTP.objects.filter(user=usr).last().otp:
                usr.is_active=True
                usr.save()
                messages.success(request,f'Account is created for {usr.username}')
                return redirect(login)
            else:
                messages.warning(request,f'You Entered a wrong OTP')
                return render(request,'register.html',{'otp':True,'usr':usr})
        form = CreateUserForm(request.POST)
        #Form Validation
        if form.is_valid():
            form.save()
            email=form.cleaned_data.get('email')
            username=form.cleaned_data.get('username')
            usr=Customer.objects.get(username=username)
            usr.email=email
            usr.username=username
            usr.is_active=False
            usr.save()
            usr_otp=random.randint(100000,999999)
            UserOTP.objects.create(user=usr,otp=usr_otp)
            mess=f'Hello\t{usr.username},\nYour OTP to verify your account for DahStyles is {usr_otp}\nThanks!'
            send_mail(
                    "welcome to DahStyles -Verify your Email",
                    mess,
                    settings.EMAIL_HOST_USER,
                    [usr.email],
                    fail_silently=False
                )
            messages.info(request,f'OTP send to your email')

            return render(request,'register.html',{'otp':True,'usr':usr})
            
        else:
            errors = form.errors
            for field, errors in errors.items():
              for error in errors:
                messages.error(request, f" {error}")
                       
    #Resend OTP
    elif (request.method == "GET" and 'username' in request.GET):
        get_usr = request.GET['username']
        if (Customer.objects.filter(username = get_usr).exists() and not Customer.objects.get(username = get_usr).is_active):
            usr = Customer.objects.get(username=get_usr)
            id = usr.id
            
            otp_usr = UserOTP.objects.get(user_id=id)
            usr_otp=otp_usr.otp
            mess = f"Hello, {usr.username},\nYour OTP is {usr_otp}\nThanks!"
            
            send_mail(
        "Welcome to DahStyles - Verify Your Email",
        mess,
        settings.EMAIL_HOST_USER,
        [usr.email],
        messages.success(request, f'OTP resend to  {usr.email}'),

        # fail_silently = False
         )
        return render(request,'register.html',{'otp':True,'usr':usr})
    else:
            errors = ''
    form=CreateUserForm()
    context = {'form': form, 'errors': errors}

    return render (request, 'register.html', context)

def logout(request):
    auth.logout(request)
    return redirect(home)

from django.shortcuts import get_object_or_404
def home(request):
    product = Product.objects.all()[:4]
    context = {'product': product}
    return render(request, 'home.html', context)

from django.shortcuts import get_object_or_404


def product_details(request, category_slug, product_slug):
    # Get the product object
    product = get_object_or_404(Product, category__slug=category_slug, slug=product_slug)

    if request.method == 'POST':
        # Get the product variations
        product_variations = []
        for key, value in request.POST.items():
            if key.startswith('variation_'):
                variation_id = int(value)
                variation = get_object_or_404(Variation, id=variation_id, product=product)
                product_variations.append(variation)

        # Get the cart object
        cart_id = _cart_id(request)
        try:
            cart = Cart.objects.get(cart_id=cart_id)
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=cart_id)

        # Add the product to the cart
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        cart_item.variations.set(product_variations)
        cart_item.quantity += 1
        cart_item.save()

        return redirect('cart')

    context ={
        'products': product
    }
    return render(request, 'details.html', context)

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)
    if current_user.is_authenticated:
        product_variations = []
        if request.method == 'POST':
            print('SFKSLDJFKLDSJFSDFDSJFKLSD',request.POST)
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(
                        product=product,
                        variation_category__iexact=key,
                        variation_value__iexact=value
                    )
                    product_variations.append(variation)
                except Variation.DoesNotExist:
                    pass
        else:
            size = request.GET.get('size')
            color = request.GET.get('color')
            
            print('======================================')
            print(size)
            print(color)
            print('=======================================')
            
            variation = Variation.objects.get(
                product=product,
                variation_category__iexact='size',
                variation_value__iexact=size
            )
            product_variations.append(variation)
        
            variation = Variation.objects.get(
                product=product,
                variation_category__iexact='color',
                variation_value__iexact=color
            )
            product_variations.append(variation)  
             
        cart, created = Cart.objects.get_or_create(cart_id=_cart_id(request),user=request.user)
        is_cart_item_exists = CartItem.objects.filter(
            product=product,
            cart=cart,
            variations__in=product_variations
        ).exists()

        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(
                product=product,
                cart=cart,
                variations__in=product_variations
            ).first()
            cart_item.quantity += 1 # increase the quantity by 1
            cart_item.save()
        else:
            cart_item = CartItem.objects.create(
                product=product,
                cart=cart,
                quantity=1,
                user=current_user
            )
            if len(product_variations) > 0:
                cart_item.variations.add(*product_variations)
                cart_item.save()
    else:
       return  redirect (login)
    return redirect('cart')




from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

@login_required(login_url='/login/')
def cart(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    
    try:
        cart_items = CartItem.objects.filter(user=request.user, is_active=True).order_by('id')
      
        for cart_item in cart_items:
            product_price = int(cart_item.product.price)
            total += product_price * int(cart_item.quantity)
            quantity += cart_item.quantity
            cart_item.price = product_price
            cart_item.save()
        
        tax = (5 * total) / 100
        grand_total = total + tax
        grand_total = format(grand_total, '.2f')
            
    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_item': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    
    return render(request, 'cart.html', context)





def remove_cart(request, product_id, cart_item_id):
    
  product = get_object_or_404(Product, id=product_id)
  
  try:
    if request.user.is_authenticated:
      cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
      cart = Cart.objects.get(cart_id=_cart_id(request))
      cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    
    if cart_item.quantity > 1:
      cart_item.quantity  -= 1
      cart_item.save()
    else:
      cart_item.delete()
      
  except:
    pass
  return redirect('cart')


def remove_cart_item(request, product_id, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, product__id=product_id)
    cart = Cart.objects.filter(id=cart_item.cart_id).first()
    if cart is not None:
        try:
            cart_item.sub_total -= cart_item.sub_total
            cart.save()
        except:
            pass
    cart_item.delete()
    return redirect('cart')

def forgetpassword(request):
    if request.method=="POST":
        email=request.POST['email']
        if Customer.objects.filter(email=email).exists():
            user=Customer.objects.get(email__exact=email)
           #reset password email
            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('reset_password_email.html', {
                'user': user,
                'domain': current_site,
             
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                 # Generate a token for a user also
                'token':default_token_generator.make_token(user),
            })
            to_email = email
            send_email=EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            send_email.send()

            messages.success(request,"Password reset email has been sent to your email")
            
            return redirect('login')
        else:
            messages.error(request,'Account does not exists')
            return redirect('login')
    return render(request,'forget.html')

def resetpassword_validate(request,uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Customer._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError,Customer.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid']=uid
        messages.success(request,"  Please reset your password")
        return redirect('resetpassword')
    else:
        messages.error(request,"This link has been expired")
        return redirect('login')

    

    
# @login_required(login_url='login')
# @never_cache   
def resetpassword(request):
   if request.method=="POST":
        password=request.POST['password']
        confirm_password=request.POST['confirm_password']
        if password == confirm_password:
            uid=request.session.get('uid')
            user= Customer.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,"Password reset successful")
            return redirect('login')
        else:
          messages.error(request,"Password not match")
          return redirect('resetPassword')
   else:
     return render (request,'resetpassword.html')


def wishlist(request):
    # wishlist_items = WishlistItem.objects.filter(wishlist__user=request.user)
    # context = {
    #     'wishlist_items': wishlist_items
    # }
    return render(request, 'wishlist.html')

@login_required(login_url='login')
def add_to_wishlist(request, product_id):
    print('================================================')
    product = get_object_or_404(Product, id=product_id)     
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist_items = wishlist.wishlistitem_set.all()
    for item in wishlist_items:
        if item.product == product:
            messages.warning(request, 'This product is already in your wishlist')
            return redirect('shop')
        
    wishlist_item = WishlistItem.objects.create(wishlist=wishlist, product=product)
    messages.success(request, 'Product added to your wishlist')
    return redirect('wishlist')


def add_wishlist(request,product_id):
    try:
        product = Product.objects.get(id=product_id)
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        item, _ = WishlistItem.objects.get_or_create(wishlist=wishlist, product=product)
        messages.success(request, 'Product added to your wishlist')
        return redirect('wishlist')
    except:
        messages.warning(request, 'Something went wrong')
        return redirect('shop')
    

def remove_from_wishlist(request, item_id):
    wishlist_item = WishlistItem.objects.get(id=item_id)
    wishlist_item.delete()
    return redirect('wishlist')


def shop(request, category_slug=None):
    # Get category and product (filtered by category if provided)
    categories = None
    product = None
    if category_slug:
        categories = get_object_or_404(Category, slug=category_slug)
        product = Product.objects.filter(category=categories, is_available=True)
    else:
        product = Product.objects.filter(is_available=True)

    # Get price range (if provided)
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        product = product.filter(price__gte=float(min_price.replace('$', '')))
    if max_price:
        product = product.filter(price__lte=float(max_price.replace('$', '')))

    # Handle sorting parameter
    sort_param = request.GET.get('sort')
    if sort_param == 'price_asc':
        product = product.order_by('price')
    elif sort_param == 'price_desc':
        product = product.order_by('-price')

    # Paginate results
    paginator = Paginator(product, 3)
    page = request.GET.get('page')
    paged_product = paginator.get_page(page)

    context = {
        'product': paged_product,
        'category_param': f"&category_slug={category_slug}" if category_slug else "",
    }
    return render(request, 'shop.html', context)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Your password was successfully updated!')
            update_session_auth_hash(request, user)
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'changepass.html', {'form': form})


def login_required_decorator(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper

change_password = login_required_decorator(change_password)

def sort_product_low_to_high(request):
    categories = None
    product = None
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if min_price is not None:
        min_price = float(min_price.replace('$', ''))

    if max_price is not None:
        max_price = float(max_price.replace('$', ''))
        
    product = Product.objects.all().filter(is_available=True).order_by('-price')
    paginator=Paginator(product,)
    page = request.GET.get('page')
    paged_product= paginator.get_page(page)
        
    if min_price is not None and max_price is not None:
        product = product.filter(price_gte=min_price, price_lte=max_price)
        
    context = {
        'product': paged_product,
        
    }

    return render(request, 'shop.html', context)


def sort_product_high_to_low(request, category_slug=None):
    categories = None
    product = None
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if min_price is not None:
        min_price = float(min_price.replace('$', ''))

    if max_price is not None:
        max_price = float(max_price.replace('$', ''))

    if category_slug is not None:
        categories = get_object_or_404(Category, slug=category_slug)
        product = Product.objects.filter(category=categories, is_available=True).order_by('-price')
        paginator=Paginator(product,3)
        page = request.GET.get('page')
        paged_product= paginator.get_page(page)
    else:
        product = Product.objects.all().filter(is_available=True).order_by('-price')
        paginator=Paginator(product,3)
        page = request.GET.get('page')
        paged_product= paginator.get_page(page)
        
    if min_price is not None and max_price is not None:
        product = product.filter(price_gte=min_price, price_lte=max_price)
        
    context = {
        'product': paged_product,
        
    }

    return render(request, 'shop.html', context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(product_name__icontains=keyword)
            
        else:
            return redirect('shop')
        
        context={
            'product':products,
        }
        
    return render(request, 'shop.html',context)




@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    state= State.objects.all()
    city = City.objects.all()
    tax = 0
    grand_total = 0
    address = AddressDetails.objects.filter(user_id= request.user)
    
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(user=request.user, is_active=True).order_by('id')
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True).order_by('id')
      
        # for cart_item in cart_items:
        #     product_price = int(cart_item.product.price)
        #     total += product_price * int(cart_item.quantity)
        #     quantity += cart_item.quantity
        #     cart_item.price = product_price
        #     cart_item.save()
        
        total = cart.get_cart_total()
        
            
    except ObjectDoesNotExist:
        pass
    
  

    context = {
        'total' : total,
        'quantity': quantity,
        'cart': cart,
        'cart_items': cart_items,
        'address': address,
        'city' : city,
        'state' :state,
        
    } 
    
    return render(request, 'checkout.html', context)





@login_required(login_url='login')
def myaccount(request):
    user = request.user
    return render(request, 'profile.html', {'user': user})

def orderbook(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'orders.html', {'orders': orders})

def viewOrder(request, id):
    order =Order.objects.filter(id=id,user=request.user).first()
    orderitems = OrderProduct.objects.filter(order=order)

    context={
        'order': order,
        'orderitems':orderitems,
    }
    return render(request,'orderview.html',context)

from django.shortcuts import get_object_or_404, redirect

def cancel_order(request, id):
    # Fetch the order object to be cancelled
    order = get_object_or_404(Order, id=id, user=request.user)

    if request.method == 'POST':
        # Update the order status to cancelled
        order.status = Order.CANCELLED
        order.save()

        # Redirect to the order details page
        return redirect('view_order', id=id)

    # If the request method is GET, render the confirmation page
    context = {'order': order}
    return render(request, 'cancel_order.html', context)


  
# @login_required(login_url='login')
# def orderbook(request):
#     orders = Order.objects.filter(user=request.user).order_by('-created_at')

#     return render(request, 'main/orders.html', {'orders': orders})
  
# def viewOrder(request, id):
#     order =Order.objects.filter(id=id,user=request.user).first()
#     orderitems = OrderProduct.objects.filter(order=order)

#     context={
#         'order': order,
#         'orderitems':orderitems,
#     }
#     return render(request,'orderview.html',context)

def updateprofile(request):
    user_id= request.user.id
    user = Customer.objects.get(pk=user_id)

    if request.method == 'POST':
        form = UpdateUserForm(request.POST, request.FILES, instance=user)
        
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('myaccount')
        else:
            messages.error(request, 'There was an error while updating your profile.')
    else:
        form = UpdateUserForm(instance=user)
        context = {'form': form}
    return render(request, 'updateprofile.html', context)

def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('manageaddress')
    else:
        form = AddressForm()
    return render(request, 'add_address.html', {'form': form})

def edit_address(request,id):
    address = get_object_or_404(AddressDetails, id=id, user=request.user)

    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect('manageaddress')
    else:
        form = AddressForm(instance=address)

    return render(request, 'edit_address.html', {'form': form})

def manageaddress(request):
    user = request.user
    add = AddressDetails.objects.filter(user_id=user.id)
    return render(request, 'manageaddress.html', {'add': add})

def deleteaddress(request,id):
    dele=AddressDetails.objects.get(id=id)
    dele.delete()
    return redirect(manageaddress)