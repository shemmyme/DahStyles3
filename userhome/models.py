from django.db import models
from admin_side.models import *
from admin_side.models import Product, Variation
from django.core.validators import MinValueValidator,MaxValueValidator
from django.contrib.auth import get_user_model
# from order.models import *

# Create your models here.




class Cart(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    cart_id = models.CharField(max_length=100, unique=True)
    date_added = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'cart'
        ordering = ['date_added']
        
        
    def get_cart_total(self):
        cart_items = CartItem.objects.filter(cart=self.id)
        price = []
        for cart_item in cart_items:
            quantity = cart_item.quantity
            price.append(cart_item.product.price * quantity)
        
        return sum(price)
        
    def get_tax(self):
        return round(0.05 * self.get_cart_total(), 2)
    
    
    def get_grand_total(self):
        total = self.get_cart_total() + self.get_tax()
        return total

    def _str_(self):
        return self.cart_id
    
 
  
class CartItem(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE,null=True)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    # price = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    razor_pay_order_id = models.CharField(max_length=100, null=True,blank=True)
    razor_pay_payment_id = models.CharField(max_length=100, null=True,blank=True)

    def sub_total(self):
        return int(self.product.price)*int(self.quantity)
    
    def _unicode_(self):
        if self.product:
            return self.product.product_name
        
    def __str__(self):
        return self.product.product_name


class City(models.Model):
    name=models.CharField( max_length=50)
 
 
    def _str_(self):
        return self.name
    
class State(models.Model):
    name= models.CharField( max_length=50)

    def _str_(self):
        return self.name
    

class Wishlist(models.Model):
    user = models.OneToOneField(Customer, on_delete=models.CASCADE)

class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    def _str_(self):
        return f"{self.wishlist.user.username}'s wishlist item: {self.product.name}"
   
