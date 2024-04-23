from django.urls import path,include
from .import views
urlpatterns = [
    path('',views.home,name='home'),
    path('women/',views.women,name='women'),
    path('men/',views.men,name='men'),
    path('product_details/',views.product_details,name='product_details'),
    path('cart/',views.cart,name='cart'),
    path('checkout/',views.checkout,name='checkout'),
    path('contact/',views.contact,name='contact'),

]