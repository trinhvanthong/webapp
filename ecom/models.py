import os
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.forms import ValidationError
from django.contrib.auth.hashers import make_password
from django.core.exceptions import PermissionDenied

# Create your models here.
def custom_upload_to(instance, filename):
    # Get the file extension from the original filename
    ext = filename.split('.')[-1]
    # Construct a new filename using the instance's product ID and the original file extension
    new_filename = f"{instance.product.id}.{ext}"
    # Return the final path where the file should be saved
    return os.path.join('./static/product_images/', new_filename)

class Customer(AbstractUser):
    # Add your additional fields here
    avatar_image = models.ImageField( null=True,upload_to='./static/imgs/')
    telephone = models.IntegerField(null=True)
    create_at = models.DateTimeField(auto_now_add=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, null=True)
    delete_at = models.DateTimeField(null=True)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"    
class Provider(models.Model):
    user = models.OneToOneField('Customer', related_name='provider_profile',on_delete=models.CASCADE)
    avatar =models.ImageField((""), upload_to='./static/profile/')  
    cover =models.ImageField((""), upload_to='./static/profile/')  
    facebook = models.TextField()
    about = models.TextField()
    provider_name = models.TextField()
    provider_email = models.TextField()
    provider_telephone=models.IntegerField(null=True)
    create_at = models.DateTimeField(auto_now_add=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, null=True)
    delete_at = models.DateTimeField(null=True)    
class Category(models.Model):
    name = models.CharField(null=False, blank=False,max_length=200)
    create_at = models.DateTimeField(auto_now_add=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, null=True)
    delete_at = models.DateTimeField(null=True)
    def __str__(self):
        return f"{self.name}"    
class Discount(models.Model):
    name = models.CharField(null=False, blank=False,max_length=200)
    desc = models.TextField()  
    discount_percent = models.DecimalField(max_digits=2, decimal_places=2)
    active = models.BooleanField(default=True)
    create_at = models.DateTimeField(auto_now_add=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, null=True)
    delete_at = models.DateTimeField(null=True)
    def __str__(self):
        return f"{self.name}"
class Product(models.Model):
    name = models.TextField(null=False, blank=False )
    provider=models.ForeignKey( Provider, on_delete=models.CASCADE)
    desc = models.TextField()  
    price = models.IntegerField( null=True)
    create_at = models.DateTimeField(auto_now_add=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, null=True)
    delete_at = models.DateTimeField(null=True)
    def __str__(self):
        return f"{self.name}"
class ProductAttribute(models.Model):
    product = models.ForeignKey( Product, on_delete=models.CASCADE)    
    size =  models.CharField(null=True, blank=True,max_length=200 ) 
    color =  models.CharField(null=True, blank=True,max_length=200 )    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    main = models.BooleanField(default=False)
    image = models.ImageField(upload_to=custom_upload_to)  # Use the 'ImageField' for file storage

    def __str__(self):
        return f"{self.product.name} - {self.image}"       
class DiscountProduct(models.Model):
    product =models.ForeignKey( Product, on_delete=models.CASCADE)
    discount =models.ForeignKey( Discount, on_delete=models.CASCADE)
    create_at = models.DateTimeField(auto_now_add=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, null=True)
    delete_at = models.DateTimeField(null=True) 
class ProductInventory(models.Model):
    product = models.ForeignKey( Product, on_delete=models.CASCADE)    
    product_attribute =models.ForeignKey( ProductAttribute, on_delete=models.CASCADE)
    quantity = models.IntegerField()    
    create_at = models.DateTimeField(auto_now_add=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, null=True)
    delete_at = models.DateTimeField(null=True)      
    def __str__(self):
        return f"{self.product.name} "    
class ProductCategory(models.Model):  
    product  = models.ForeignKey(Product,on_delete=models.CASCADE)    
    category = models.ForeignKey(Category, on_delete=models.CASCADE)     
    create_at = models.DateTimeField(auto_now_add=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, null=True)
    delete_at = models.DateTimeField(null=True)
    def __str__(self):
        return f"{self.category.name}---{self.product.name}"      
class PaymentDetails(models.Model):
    order= models.IntegerField()
    amount =models.IntegerField()
    provider =models.CharField( max_length=200)    
    status = models.CharField( max_length=50)    
    create_at =models.DateTimeField
    modified_at = models.DateTimeField  
class OrderDetails(models.Model):
    user = models.OneToOneField(Customer,null= False, on_delete=models.CASCADE)
    total = models.DecimalField( max_digits=5, decimal_places=2)
    payment = models.ForeignKey(PaymentDetails, on_delete= models.CASCADE)
    create_at = models.DateTimeField(auto_now_add=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, null=True)
    delete_at = models.DateTimeField(null=True) 
class OrderItems(models.Model):
    order = models.ForeignKey(OrderDetails,on_delete=models.CASCADE)  
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.IntegerField() 
    create_at = models.DateTimeField(auto_now_add=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, null=True)
    delete_at = models.DateTimeField(null=True)      
class CustomerAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)  
    address_line1 = models.CharField( max_length=250)
    address_line2 = models.CharField( max_length=250)
    city = models.CharField( max_length=50)
    postal_code = models.CharField( max_length=50)
    country = models.CharField( max_length=50)
class ProviderAddress(models.Model):
    name = models.CharField(null=False, blank=False,max_length=200)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)  
    address_line = models.CharField( max_length=250)
    area = models.CharField( max_length=250)
    city = models.CharField( max_length=50)
    district = models.CharField( max_length=50)
class ShoppingSession(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)  
    total =models.IntegerField( null=True)
    create_at = models.DateTimeField(auto_now_add=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, null=True)

class Cart_items(models.Model):
    session = models.ForeignKey(ShoppingSession, on_delete=models.CASCADE)         
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    create_at = models.DateTimeField(auto_now_add=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, null=True)
    delete_at = models.DateTimeField(null=True)