from django.db import models
from django.urls import reverse
from django.contrib.auth.models import Permission,Group 
from django.contrib.auth.models import AbstractUser
from PIL import Image

# Create your models here.
class Customer(AbstractUser):
    email = models.EmailField(unique=True)
    profile_pic = models.ImageField(upload_to='profile_pics', null=True, blank=True)
    phone = models.CharField(max_length=10, default=1234567890, null=True, blank=True)
    address = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    pincode = models.IntegerField(null=True, blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='customers')
    groups = models.ManyToManyField(Group, related_name='customers')

class UserOTP(models.Model):
    user=models.ForeignKey(Customer,on_delete=models.CASCADE)
    time_st=models.DateTimeField(auto_now=True)
    otp=models.IntegerField()

class AddressDetails(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    order_address = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def full_address(self):
        return f"{self.order_address},{self.city}, {self.state}, {self.country}, PIN: {self.zip_code}"
    
    def str(self):
        return self.user.username

class Category(models.Model):
  category_name = models.CharField(max_length=50, unique=True)
  slug = models.SlugField(max_length=100, unique=True)
  category_offer = models.IntegerField(default=0)
  description = models.TextField(max_length=255, blank=True)
  cat_image = models.ImageField(upload_to='photos/categories', blank=False)
  modified_at = models.DateTimeField(auto_now=True)
 
   
      
  class Meta:
        verbose_name        = 'category'
        verbose_name_plural = 'categories'

  def get_url(self):
        return reverse('product_by_category',args=[self.slug])
  
   
  def __str__(self):
        return self.category_name
  
 


    
class Product(models.Model):
  
  UNIT = (
          ('piece', 'piece'),    
          )
  product_name = models.CharField(max_length=200, unique=True)
  slug = models.SlugField(max_length=255, unique=True)
  description = models.TextField(max_length=500, blank=True)
  price = models.IntegerField()
  product_offer = models.IntegerField(default = 0)
  unit = models.CharField(max_length=50,choices=UNIT,default='piece')
  image_1 = models.ImageField(upload_to='photos/products', blank=False)
  image_2 = models.ImageField(upload_to='photos/products', blank=True)
  image_3 = models.ImageField(upload_to='photos/products', blank=True)
  image_4 = models.ImageField(upload_to='photos/products', blank=True)
  stock = models.IntegerField()
  is_available = models.BooleanField(default=True)
  is_featured = models.BooleanField(default=False)
  category = models.ForeignKey(Category, on_delete=models.CASCADE)
  created_date = models.DateTimeField(auto_now_add=True)
  modified_date = models.DateTimeField(auto_now=True)
  
  def save(self,*args,**kwargs):
    super().save(*args,**kwargs)
    
    for i in range(1, 4):
      image_attr = f"image_{i}"
      image_path = getattr(self, image_attr).path
      
      if image_path:
        img=Image.open(image_path)
     
        if img.height>300 or img.width>300:
          output_size = (600,600)
          img.thumbnail(output_size)
          img.save(image_path)  
  
  def get_url(self):
    return reverse('product_details', args=[self.category.slug, self.slug])
  
  def __str__(self):
    return self.product_name

  
  
  
class VariationManager(models.Manager):
  
  def colors(self):
    return super(VariationManager, self).filter(variation_category='color', is_active=True)
  
  def sizes(self):
    return super(VariationManager, self).filter(variation_category='size', is_active=True)
  

  
variation_category_choice =  (
    ('size','size'),
    ('color','color'),
    
)

class Variation(models.Model):
  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  variation_category = models.CharField(max_length=100, choices=variation_category_choice)
  variation_value = models.CharField(max_length=100)
  price_multiplier = models.IntegerField(default=1)
  is_active = models.BooleanField(default=True)
  created_date = models.DateTimeField(auto_now=True)
  
  objects = VariationManager()
  
  def __str__(self):
    return self.variation_value