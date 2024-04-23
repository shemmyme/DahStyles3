from django.shortcuts import render,redirect
from .models import *
from django.utils.text import slugify
from django.contrib import auth,messages
from userhome.views import *
from .models import *
from order.models import *
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import never_cache
from django.shortcuts import get_object_or_404
from django.db.models import Sum, DateField
from datetime import datetime, timedelta
from django.db.models.functions import TruncDay, Cast
from django.db.models import Sum, Q, FloatField
from django.db.models.functions import Cast
from django.core.paginator import Paginator
import razorpay
from razorpay.errors import BadRequestError
from .form import *


# from django.http import HttpResponse
# from django.template.loader import get_template




# Create your views here.

# def admin_panel(request):
    
#     return render(request,'admin_panel.html')
@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def admin_panel(request):
    sales = OrderProduct.objects.all().count()
    users = Customer.objects.all().count()
    recent_sales = Order.objects.order_by('-id')[:5]

    # Graph setting
    # Getting the current date
    today = datetime.today()
    date_range = 8

    # Get the date 7 days ago
    four_days_ago = today - timedelta(days=date_range)

    #filter orders based on the date range
    payments = Payment.objects.filter(created_at__gte=four_days_ago, created_at__lte=today)

    # Getting the sales amount per day
    sales_by_day = payments.annotate(day=TruncDay('created_at')).values('day').annotate(total_sales=Sum('amount_paid')).order_by('day')

    
    context = {
        'sales' : sales,
        'users' : users,
        'sales_by_day' : sales_by_day,
        'recent_sales' :recent_sales,
    }
    return render(request, 'dashboard.html',context)
  
@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def adminprofile(request):
  
    return render(request,'adminprofile.html')

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def addProduct(request):
  if request.method == 'POST':
    form = ProductForm(request.POST, request.FILES)
    if form.is_valid():
      form.save()
      messages.success(request, 'Product added successfully.')
      return redirect('products')
    else:
      messages.error(request, 'Invalid input!!!')
      return redirect('addProduct')
  else:
    form = ProductForm()
    context = {
      'form':form,
    }
    return render(request, 'addprodect.html', context)

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def editProduct(request, id):
  product = Product.objects.get(id=id)
  
  if request.method == 'POST':
    form = ProductForm(request.POST, request.FILES, instance=product)
    
    if form.is_valid():
      form.save()
      messages.success(request, 'Product edited successfully.')
      return redirect('products')
    else:
      messages.error(request, 'Invalid input')
      
  form =   ProductForm(instance=product)
  context = {
    'form':form,
    'product':product,
  }
  return render(request, 'adminprodectedit.html', context)

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def deleteProduct(request, id):
  product = Product.objects.get(id=id)
  product.delete()
  return redirect('products')


@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def variantsselection(request):
    # if request.method == "POST":
    #    Sizefield=Sizefield
       

    #     # slug = slugify(name)

    #     category = Category(category_name=name, description=description, cat_image= cat_image)
    #     category.save()

    #     msg = "Category added"
    #     # return redirect('adminapp:viewcategory')
    return render(request,'variants_selection.html')



@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def admincategory(request):
    categories = Category.objects.all().order_by('id')
    paginator = Paginator(categories, 3)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context ={
      'catt': page_obj
    }

    return render(request, 'admincategory.html', context)


@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def addCategory(request):
  if request.method == 'POST':
    form = CategoryForm(request.POST, request.FILES)
    if form.is_valid():
      form.save()
      messages.success(request, 'Category added successfully.')
      return redirect(admincategory)
    else:
      messages.error(request, 'Invalid input!!!')
      return redirect('addCategory')
  else:
    form = CategoryForm()
   

    return render(request, 'addcategory.html', locals())
  
@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def cat_search(request):
    print(request.GET)
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            catt = Category.objects.filter(category_name__icontains=keyword)
            
            if not catt:
                message = "No products found for the keyword entered."
                context = {
                    'message': message
                }
                return render(request, 'admincategory.html', context)
                
    context = {
        'catt': catt
    }
        
    return render(request, 'admincategory.html', context)
  

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def editCategory(request, category_slug):
    # Retrieve the category object using its slug
    category = Category.objects.get(slug=category_slug)

    if request.method == 'POST':
        # Create a form instance with the submitted data and files,
        # and bind it to the category instance
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category edited successfully.')
            return redirect(admincategory)
        else:
            # If the form is invalid, display error messages
            messages.error(request, 'Invalid input')

    # Create a new form instance with the category object
    form = CategoryForm(instance=category)

    context = {
        'form': form,
        'category': category,
    }
    return render(request, 'categoryedit.html', context)

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def adminupdate(request):
    user_id= request.user.id
    user = Customer.objects.get(pk=user_id)

    if request.method == 'POST':
        form = UpdateUserForm(request.POST, request.FILES, instance=user)
        
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('adminprofile')
        else:
            messages.error(request, 'There was an error while updating your profile.')
    else:
        form = UpdateUserForm(instance=user)
        context = {'form': form}
    return render(request, 'adminupdate.html', context)
  
@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def addaddress(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('adminmanage')
    else:
        form = AddressForm()
    return render(request, 'addaddress.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def editad(request,id):
    address = get_object_or_404(AddressDetails, id=id, user=request.user)

    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect('adminmanage')
    else:
        form = AddressForm(instance=address)

    return render(request, 'editad.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def adminmanage(request):
    user = request.user
    add = AddressDetails.objects.filter(user_id=user.id)
    return render(request, 'adminmanage.html', {'add': add})

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def deletead(request,id):
    dele=AddressDetails.objects.get(id=id)
    dele.delete()
    return redirect(manageaddress)


@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def deleteCategory(request, slug):
    category = Category.objects.get(slug=slug)
    category.delete()
    messages.success(request, 'Category deleted successfully.')
    return redirect(admincategory)


@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def products(request):
    products_list = Product.objects.all().order_by('-id')
    paginator = Paginator(products_list, 4)  

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj
        
    }
    return render(request, 'prodects.html', context)


@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def adminproductedit(request,product):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
    
        if form.is_valid():
            form.save()
            messages.success(request, 'Product edited successfully.')
        return redirect('products')
    else:
      messages.error(request, 'Invalid input')
      
    form =   ProductForm(instance=product)
    context = {
        'form':form,
        'product':product,
  }

    return render(request,'adminprodectedit.html',context)

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def deleteprodect(request,product_id):

    dele=Product.objects.get(id=product_id)
    dele.delete()


    return redirect('prodects')

from django.core.paginator import Paginator

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def product_variations(request):
    variations = Variation.objects.all().order_by('product')
    paginator = Paginator(variations, 2) # Show 25 variations per page
    page = request.GET.get('page')
    variations = paginator.get_page(page)
    context = {
        'variations': variations,
    }
    return render(request, 'product_variations.html', context)

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def add_product_variation(request):
  
  if request.method == 'POST':
    form = VariationForm(request.POST)
    if form.is_valid():
      form.save()
      messages.success(request, 'Variation added successfully.')
      return redirect('product_variations')
    else:
      messages.error(request, 'Invalid input!!!')
      return redirect('add_product_variations')
    
  form = VariationForm()
  context = {
    'form':form
  }
  return render(request, 'addvariation.html', context)

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def edit_product_variation(request, id):
  variation = Variation.objects.get(id=id)
  
  if request.method == 'POST':
    form = VariationForm(request.POST, instance=variation)
    
    if form.is_valid():
      form.save()
      messages.success(request, 'Variation edited successfully.')
      return redirect('product_variations')
    else:
      messages.error(request, 'Invalid input')
      return redirect('edit_product_variation')
      
  form =   VariationForm(instance=variation)
  context = {
    'form':form,
    'variation':variation,
  }
  return render(request, 'editvariation.html', context)

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def delete_product_variation(request, id):
    variation = Variation.objects.get(id=id)
    variation.delete()
    messages.success(request, 'Variation deleted successfully!!!')
    return redirect('product_variations')


@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def sales(request):
    return render(request, 'sales.html')

from django.core.paginator import Paginator

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def list_users(request):
    user_list = Customer.objects.all().order_by('id')
    paginator = Paginator(user_list, 5) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'users.html', {'page_obj': page_obj})


@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def blockuser(request, id):
    # user = get_object_or_404(User, id=id)
    user=Customer.objects.get(id=id)
    if user.is_active:
        user.is_active = False
        messages.success(request, "user has been blocked.")
    else:
        user.is_active = True
        messages.success(request, "user has been unblocked.")
    user.save()
    return redirect(list_users)

def admin_login(request):
    if request.method == 'POST':
        username=request.POST['username']
        password=request.POST['password']
        user=auth.authenticate(password=password,username=username)
        if user is not None:
            if user.is_superuser:
                auth.login(request, user)
                return redirect(admin_panel)
            else:
                return redirect(admin_login)
        else:
            return redirect(admin_login)

    return render(request,'admin_login.html')

def admin_logout(request):
    auth.logout(request)
    return redirect(admin_login)


@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def manage_order(request):
    orders=Order.objects.all().order_by('-id')
    paginator = Paginator(orders, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number) 
    
    return render(request, 'manageorder.html', locals())

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def manage_order_conf(request):
    
    return render(request,'manage_order_conf.html')

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def orderdetails(request, id):
    orders=Order.objects.get(pk=id)
    products = OrderProduct.objects.filter(order=orders)
    addrs =orders.address
    context = {
        'product': products,
        'addrs': addrs,
        'order': orders
    }
    return render(request, 'orderdetails.html',context)

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def searchorder(request):
    keyword = request.GET.get('name')
    print(keyword)
    orders = Order.objects.filter(Q(address__firstname__icontains=keyword) | Q(address__email__icontains=keyword) | Q(status__icontains=keyword) | Q(payment__payment_method__icontains=keyword) | Q(order_number__icontains=keyword)).order_by('-id')
    paginator = Paginator(orders, 8)
    page_numebr = request.GET.get('page')
    page_obj = paginator.get_page(page_numebr) 
    return render(request, 'manageorder.html', locals())

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def update_order(request, id):
    if request.method == 'POST':
        order = Order.objects.get(id=id)
        status = request.POST.get('status')
        if(status):
            order.status = status
            order.save()
        if status  == "Delivered":
            try:
                payment = Payment.objects.get(payment_id = order.order_number, status = False)
                print(payment)
                if payment.payment_method == 'Cash on Delivery':
                    payment.paid = True
                    payment.save()
            except:
                pass
    return redirect('manage_order')

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def admincancelOrder(request, id):

    client = razorpay.Client(auth=("rzp_test_aCOPLFUFmC265M", "xOMWffWBSmuJi5y06YT3aq4N"))
    try:
        order = Order.objects.get(id=id)
    except Order.DoesNotExist:
        # Handle the case where the order does not exist
        order = None
    
    if order is None:
        # Render an error message if the order does not exist
        messages.warning(request,'The order you are trying to cancel does not exist.')
        return redirect(manage_order)
    
    payment=order.payment
    msg=''
    
    if (payment.payment_method == 'Paid by Razorpay'):
        payment_id = payment.payment_id
        amount = payment.amount_paid
        amount= amount*100
        try :
            captured_amount = client.payment.capture(payment_id,amount)
        except BadRequestError as e:
            # Handle a BadRequestError from Razorpay
            captured_amount = None
            messages.warning(request,'The payment has not been captured,We cant Refund the money')
            return redirect(manage_order)
        #   except ServerError as e:
              # Handle a ServerError from Razorpay
        #   captured_amount = None
            # msg = "Server error occurred while capturing the payment."

        if captured_amount is not None and captured_amount['status'] == 'captured' :
            refund_data = {
                "payment_id": payment_id,
                "amount": amount,  # amount to be refunded in paise
                "currency": "INR",
            }
            
            refund = client.payment.refund(payment_id, refund_data)
            #  except BadRequestError as e:
            #      # Handle a BadRequestError from Razorpay
            #      refund = None
            #      msg = "Bad request error occurred while processing the refund."
            #  except ServerError as e:
            #      # Handle a ServerError from Razorpay
            #      refund = None
            #      msg = "Server error occurred while processing the refund."
            print(refund)
            
            if refund is not None:
                current_user=request.user
                order.refund_completed = True
                order.status = 'Cancelled'
                payment = order.payment
                payment.refund_id = refund['id']
                payment.save()
                order.save()
                messages.success(request,'The order has been successfully cancelled and amount has been refunded!')
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
                messages.warning(request,'The order is not cancelled because the refund could not be completed now. Please try again later. If the issue continues, CONTACT THE SUPPORT TEAM!')
                pass
        else :
            if(payment.paid):
                order.refund_completed = True
                order.status = 'Cancelled'
                messages.success(request,'THE ORDER HAS BEEN SUCCESSFULLY CANCELLED!')
                order.save()
            else:
                order.status = 'Cancelled'
                order.save()
                messages.success(request,'The payment has not been recieved yet. But the order has been cancelled.!')
    else :
        order.status = 'Cancelled'
        messages.success(request,'THE ORDER HAS BEEN SUCCESSFULLY CANCELLED!')
        order.save()
    return redirect(manage_order)
