from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views 

urlpatterns = [
    path('',views.home,name='home'),
    path('home/',views.home,name='home'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    path('register/', views.register,name='register'),
    # path('shop/',views.shop ,name='shop'),
    # path('details/<int:id>',views.details ,name='details'),
    # path('profile/',views.profile ,name='profile'),
    # path('cart/',views.cart ,name='cart'),
    # path('checkout/',views.checkout ,name='checkout'),
    # path('contact/',views.contact ,name='contact'),
    # path('add_to_cart/<int:product_id>/',views.add_to_cart,name='add_to_cart'),
    # path('show_cart/',views.show_cart,name='show_cart'),
    path('shop',views.search,name='search'),
    path('change-password/',views. change_password, name='change_password'),
    path('forgetpassword/',views.forgetpassword,name='forgetpassword'),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),
    path('resetpassword/',views.resetpassword,name='resetpassword'),
    # path('remove_from_cart/<int:cart_id>/<int:product_id>/',views.remove_from_cart,name='remove_from_cart'),
    path('',views.home,name='home'),
    # path('us_product/',views.us_products,name='us_products'),
    path('cart/',views.cart,name='cart'),
    path('add_cart/<int:product_id>/', views.add_cart, name='add_cart'),
    path('remove_cart/<int:product_id>/<int:cart_item_id>/', views.remove_cart, name='remove_cart'),
    path('remove_cart_item/<int:product_id>/<int:cart_item_id>/', views.remove_cart_item, name='remove_cart_item'),
    # path('filterplace/search/',views.search,name='search'),
    path('myaccount/',views.myaccount,name='myaccount'),
    path('orderbook/', views.orderbook, name='orderbook'),
    path('vieworder/<int:id>/',views.viewOrder, name='vieworder'),
    path('shop/', views.shop, name='shop'),
    path('shop/<slug:category_slug>/', views.shop, name='product_by_category'),
    path('shop/<slug:category_slug>/<slug:product_slug>/', views.product_details, name='product_details'),
    path('wishlist/<slug:category_slug>/<slug:product_slug>/', views.product_details, name='product_details'),
    path('shop/', views.sort_product_low_to_high, name='sort_products_low_to_high'),
    path('shop/ ', views.sort_product_high_to_low, name='sort_products_high_to_low'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('remove_from_wishlist/<int:item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('checkout/',views.checkout, name='checkout'),
    path('add_address/',views.add_address,name='add_address'),
    path('updateprofile/', views.updateprofile, name='updateprofile'),
    path('manageaddress/',views.manageaddress,name='manageaddress'),
    path('deleteaddress/<int:id>/',views.deleteaddress,name='deleteaddress'),
    path('edit_address/<int:id>/', views.edit_address, name='editaddress'),
    
    
    path('add_wishlist/<int:product_id>/', views.add_wishlist, name='add_wishlist'),
 
    


    
#reset password#
    path('password_reset/',auth_views.PasswordResetView.as_view(),name='password_reset'),
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),

    


] + static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)
