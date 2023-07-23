from .models import *
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# 
# 
class CustomerSerializer(ModelSerializer):
    class Meta:
        model = Customer
        fields ='__all__'
        
class ProviderSerializer(ModelSerializer):
    class Meta:
        model = Provider
        fields ='__all__'

class ProviderAddressSerializer(ModelSerializer):
    provider = ProviderSerializer()
    class Meta:
        model = ProviderAddress
        fields ='__all__'
        depth = 1       
class CustomerSerializer(ModelSerializer):
    class Meta:
        model = Customer
        fields ='__all__'
        depth = 1             
class DiscountSerializer(ModelSerializer):
    class Meta:
        model = Discount
        fields ='__all__'
        depth = 1             
        
class DiscountProductSerializer(ModelSerializer):
    class Meta:
        model = DiscountProduct
        fields =['discount','id'    ]
        depth = 1             
        
class CustomerAddressSerializer(ModelSerializer):
    customer = CustomerSerializer()
    class Meta:
        model = CustomerAddress
        fields ='__all__'
        depth = 1           
        
class ProductSerializer(ModelSerializer):
    class Meta:
        model= Product
        fields =['id']        
        
class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields= '__all__'        

class ProductCategorySerializer(ModelSerializer):
    category = CategorySerializer()
    class Meta:
        model = ProductCategory
        fields =['id','category']    
        depth = 1           
class ProductAttributeSerializer(ModelSerializer):
    class Meta:
        model = ProductAttribute  
        fields = ['size','color']  
class ProductInventorySerializer(ModelSerializer):
    class Meta:
        model = ProductInventory
        fields = ['product_attribute','quantity']  
        depth = 1   
class ProductImageSerializer(ModelSerializer):
    class Meta:
        model =ProductImage
        fields ='__all__'    
class CartItemSerializer(ModelSerializer):
    product_image =SerializerMethodField()    
    class Meta:
        model =Cart_items
        fields ='__all__'   
        depth = 1 
    def get_product_image(self,obj):
        images_queryset = ProductImage.objects.filter(product=obj.product,main=True)
        serializer = ProductImageSerializer(images_queryset, many=True, read_only=True)
        return serializer.data              
class ShoppingSessionSerializer(ModelSerializer):
    cart_items = SerializerMethodField()
    class Meta:
        model =ShoppingSession
        fields = '__all__'
    def get_cart_items(self,obj):
        cart_items_queryset =Cart_items.objects.filter(session=obj.id)
        serializer = CartItemSerializer(cart_items_queryset, many=True, read_only=True)  
        return serializer.data
class AllProductSerializer(ModelSerializer):
    category = SerializerMethodField()
    images = SerializerMethodField()
    inventory = SerializerMethodField()
    discount =SerializerMethodField()
 
    provider_infor = SerializerMethodField()  
    class Meta:
        model = Product
        fields = '__all__'
    def get_category(self, obj):
        category_queryset = ProductCategory.objects.filter(product=obj.id)
        serializer = ProductCategorySerializer(category_queryset, many=True, read_only=True)
        return serializer.data
    def get_inventory(self, obj):
        inventory_queryset = ProductInventory.objects.filter(product=obj.id)
        serializer = ProductInventorySerializer(inventory_queryset, many=True, read_only=True)
        return serializer.data
    def get_images(self, obj):
        images_queryset = ProductImage.objects.filter(product=obj.id)
        serializer = ProductImageSerializer(images_queryset, many=True, read_only=True)
        return serializer.data
    def get_discount(self, obj):
        discount_queryset = DiscountProduct.objects.filter(product=obj.id)
        serializer = DiscountProductSerializer(discount_queryset, many=True, read_only=True)
        return serializer.data
    def get_provider_infor(self,obj):
        provider_queryset = obj.provider
        serializer = ProviderSerializer(provider_queryset, read_only=True)
        return serializer.data        
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()        