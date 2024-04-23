from django.contrib import admin
from django.urls import path,include
from .import views


urlpatterns = [
   
    path('confirmation/',views.confirmation, name='confirmation'),
    path('confirmation/place_order/', views.placeOrder, name='place_order'),     
    path('order-complete/<str:ordernumber>/',views.orderComplete, name='order_complete'),
    path('success/',views.success, name='success'),
    path('proceed_to_pay/',views.razorPayCheck,name='razorpaycheck'),
    path('cancelOrder/',views.cancelOrder, name='cancelOrder'),
]