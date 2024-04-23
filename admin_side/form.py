from django import forms
from .models import *
from django.utils.safestring import mark_safe
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import UserChangeForm

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password):
            return user

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None




#regitration

class CreateUserForm(UserCreationForm):
   password1=forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Enter Password',                                            'class':'form-control',
                                         'style':'max-width:300px;  margin-left:115px'}))
   password2=forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Confirm Password',                                            'class':'form-control',
                                         'style':'max-width:300px;  margin-left:115px'}))
   class Meta:
        model = Customer
        fields = ['username', 'email','password1', 'password2']
        widgets = { 
            'username': forms.TextInput(attrs=
                                        {'placeholder': 'Username',
                                         'class':'form-control',
                                         'style':'max-width:300px; margin-left:115px'
                                         
                                         }),
            'email': forms.TextInput(attrs={'placeholder': 'Email',
                                            'class':'form-control',
                                         'style':'max-width:300px;  margin-left:115px'}),
            
             }

class UpdateUserForm(UserChangeForm):
    

    class Meta:
        model = Customer
        fields = [ 'phone', 'first_name', 'profile_pic','last_name', 'address','city', 'state', 'pincode']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Enter Your First Name','class':'form-control'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Enter Your Last Name','class':'form-control'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Enter Your Phone Number','class':'form-control'}),
            'address': forms.TextInput(attrs={'placeholder': 'Enter Your Address','class':'form-control'}),
            'state': forms.TextInput(attrs={'placeholder': 'Enter Your State','class':'form-control'}),
            'pincode': forms.NumberInput(attrs={'placeholder': 'Enter Your Pincode','class':'form-control'}),
            'city': forms.TextInput(attrs={'placeholder': 'Enter Your City','class':'form-control'}),




         }


        
form = UpdateUserForm(initial={'city': Customer.username})

class AddressForm(forms.ModelForm):
    class Meta:
        model = AddressDetails
        fields = ('first_name', 'last_name', 'phone', 'email', 'order_address', 'city', 'state', 'country', 'zip_code')
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Enter Your First Name','class':'form-control'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Enter Your Last Name','class':'form-control'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Enter Your Phone Number','class':'form-control'}),
            'country': forms.TextInput(attrs={'placeholder': 'Enter Your Address','class':'form-control'}),
            'state': forms.TextInput(attrs={'placeholder': 'Enter Your State','class':'form-control'}),
            'zip_code': forms.NumberInput(attrs={'placeholder': 'Enter Your Pincode','class':'form-control'}),
            'city': forms.TextInput(attrs={'placeholder': 'Enter Your City','class':'form-control'}),
            'email': forms.TextInput(attrs={'placeholder': 'Enter Your Email','class':'form-control'}),
            'order_address': forms.TextInput(attrs={'placeholder': 'Landmark','class':'form-control'}),
            
            
        }

class CategoryForm(forms.ModelForm):
    class Meta:
         model = Category
         fields = ['category_name', 'slug','description', 'cat_image',]
        
    def __init__(self, *args, **kwargs):
        super(CategoryForm,self).__init__(*args, **kwargs)
        for field  in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
# class SubCategoryForm(forms.ModelForm):
#     class Meta:
#          model = Sub_Category
#          fields = ['sub_category_name', 'slug', 'description', 'category', 'is_featured',]
         
        
#     def __init__(self, *args, **kwargs):
#         super(SubCategoryForm,self).__init__(*args, **kwargs)
#         for field  in self.fields:
#             self.fields[field].widget.attrs['class'] = 'form-control'
#             self.fields['is_featured'].widget.attrs['class'] = 'form-check-input small-checkbox'       

    


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'slug', 'description', 'price', 'unit', 'image_1', 'image_2', 'image_3', 'image_4', 'stock',
                  'is_available', 'is_featured', 'category']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['price'].widget.attrs['min'] = 0
        self.fields['stock'].widget.attrs['min'] = 0
        self.fields['category'].widget.attrs['onchange'] = "getval(this);"
        self.fields['is_available'].widget.attrs['class'] = 'form-check-input small-checkbox'
        self.fields['is_featured'].widget.attrs['class'] = 'form-check-input small-checkbox'
        


        for field_name, field in self.fields.items():
            classes = field.widget.attrs.get('class', '')
            classes += ' form-control'
            field.widget.attrs['class'] = classes.strip()

        # Add Bootstrap styles to the form labels
        self.label_suffix = mark_safe('<span class="text-primary">*</span>')
        

            
class VariationForm(forms.ModelForm):
    class Meta:
        model = Variation
        fields = ['product', 'variation_category', 'variation_value', 'is_active']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'variation_category': forms.Select(attrs={'class': 'form-control'}),
            'variation_value': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
    def __init__(self, *args, **kwargs):
        super(VariationForm,self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        self.fields['is_active'].widget.attrs['class'] = 'form-check-input'

