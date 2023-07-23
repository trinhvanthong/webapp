import json
import datetime
import logging
from django.db import transaction
from pytz import timezone
from .models import *
from .serializers import *
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response
from rest_framework.decorators import api_view , permission_classes
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.encoding import DjangoUnicodeDecodeError, force_str
from urllib.parse import urlencode
from django.shortcuts import redirect
from email.message import EmailMessage
import ssl
import smtplib
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
# Create your views here.
email_sender ='navhnirt@gmail.com'
email_password='bgqfyegbdgcseucn'
subject ='verify your account'
em =EmailMessage()
em['From']=email_sender
em['Subject']=subject

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['last_name'] =user.last_name  
        token['id'] =user.id  
        token['first_name'] =user.first_name  
        token['phone_number'] =user.telephone 
        token['email'] =user.email 
        if(Provider.objects.filter(user=user)):
            token['is_provider'] = True
        else:
            token['is_provider'] = False
        return token
        
from django.shortcuts import redirect
from urllib.parse import urlencode



class RegisterView(APIView):
    def post(self, request):
        serializer = CustomerSerializer(data=request.data)

            
        if serializer.is_valid():
            if len(serializer.validated_data['password'])<8 or serializer.validated_data['password'] !=request.data['repassword']:
                error_messages = ' Mật khẩu của bạn phải dài tối thiểu 8 ký tự và trùng khớp với mật khẩu được nhập lại'
                query_params = urlencode({'error': error_messages})
                redirect_url = f"http://localhost:3000/SignUp?{query_params}"
                return redirect(redirect_url)
            password = make_password(serializer.validated_data['password'])
            serializer.validated_data['password'] = password
            email_receiver = serializer.validated_data['email']
            
            # Generate a token for the user
            user = serializer.save()
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            # Set the token expiration time (e.g., 24 hours from now)
            expiration_time = datetime.datetime.now() + datetime.timedelta(hours=3)
            expiration_timestamp = int(expiration_time.timestamp())
            
            # Prepare the registration URL with token, user ID, and expiration timestamp
            registration_url = request.build_absolute_uri(
                reverse('registration-confirm') + f'?uid={uid}&token={token}&expires={expiration_timestamp}'
            )
            
            # Prepare email content
            email_subject = "Registration Confirmation"
            email_body = f"Thank you for registering. Please click the link below to complete your registration:\n\n{registration_url}"
            
            # Create EmailMessage object
            email_message = EmailMessage()
            email_message['Subject'] = email_subject
            email_message['From'] = email_sender
            email_message['To'] = email_receiver
            email_message.set_content(email_body)
            
            # Connect to SMTP server and send the email
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(email_sender, email_password)
                smtp.send_message(email_message)
            
            # Redirect to http://localhost:3000/Login
            return redirect('http://localhost:3000/Login')
        error_messages = list(serializer.errors.values())
        query_params = urlencode({'error': error_messages})
        redirect_url = f"http://localhost:3000/SignUp?{query_params}"
        return redirect(redirect_url)
def registration_confirm(request):   
    User = get_user_model()
    uidb64 = request.GET.get('uid')
    token = request.GET.get('token')
    
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist, DjangoUnicodeDecodeError):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        # Perform the registration confirmation logic here
        user.is_active = True
        user.save()
        shopping_session, created = ShoppingSession.objects.get_or_create(
                customer=user,
                defaults={"total": 0},  # You can adjust the default total as needed
            )
        shopping_session.save()
        return redirect('http://localhost:3000/Login')  # Redirect to a success page
    else:
        return redirect('http://localhost:3000/Login')# Redirect to an error page

    # Get the current date and time in the timezone you desire

class ProviderRegisterView(APIView):
    def post(self, request):
        customer_id = request.data.get('customer_id')
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({'error': 'Invalid customer ID'}, status=400)
        if hasattr(customer, 'provider_profile'):
            return Response({'error': 'Customer is already a provider'}, status=status.HTTP_409_CONFLICT)
        provider = Provider.objects.create(user=customer)
        avatar_file = request.FILES.get('profile-photo-upload')
        if avatar_file:
            avatar_filename = f"{provider.id}_avatar.{avatar_file.name.split('.')[-1]}"
            provider.avatar.save(avatar_filename, avatar_file, save=True)

        cover_file = request.FILES.get('cover-photo')
        if cover_file:
            cover_filename = f"{provider.id}_cover.{cover_file.name.split('.')[-1]}"
            provider.cover.save(cover_filename, cover_file, save=True)

        provider.facebook = 'https://www.facebook.com/'+request.data.get('facebook')
        provider.about = request.data.get('about')
        provider.provider_name = request.data.get('store_name')
        provider.provider_email = request.data.get('email')
        provider.provider_telephone = request.data.get('provider_telephone')
        provider.save()
        provider_address = ProviderAddress.objects.create(provider=provider)
        provider_address.name = 'default'
        provider_address.address_line = request.data.get('address_line')
        provider_address.district = request.data.get('district')
        provider_address.city = request.data.get('city')
        provider_address.area = request.data.get('area')
        provider_address.save()
        token_data=MyTokenObtainPairSerializer.get_token(customer)
        
        return Response({
            str(token_data)
        })

class AddProduct(APIView):
    def post(self, request):
        customer_id = request.data.get('customer_id')
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({'error': 'Invalid customer ID'}, status=400)

        provider = Provider.objects.filter(user=customer).first()
        if not provider:
            return Response({'error': 'Provider not found'}, status=400)

        try:
            with transaction.atomic():
                product = Product.objects.create(
                    provider=provider,
                    name=request.data.get('product_name'),
                    desc=request.data.get('about'),
                    price=int(request.data.get('price', 0)),
                )

                main_image = request.FILES.get('file')
                if main_image:
                    product_main_image = ProductImage.objects.create(product=product, main=True, image=main_image)

                additional_photos_count = int(request.data.get('len', 0))
                for i in range(additional_photos_count):
                    image = request.FILES.get(f"additional_photo_{i}")
                    if image:
                        ProductImage.objects.create(product=product, main=False, image=image)

                if 'product_attribute' in request.data:
                    product_attributes = json.loads(request.data.get('product_attribute'))
                    for color, sizes in product_attributes.items():
                        for size, quantity in sizes.items():
                            product_attribute = ProductAttribute.objects.create(product=product, color=color, size=size)
                            ProductInventory.objects.create(
                                product=product,
                                product_attribute=product_attribute,
                                quantity=int(quantity),
                            )

                return Response({'message': 'Product created successfully'}, status=201)

        except Exception as e:
            # Log the error here
            return Response({'error': 'An error occurred while processing the request'}, status=500)
class ProviderDetailView(generics.RetrieveAPIView):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    def get_object(self):
        user_id = self.kwargs.get('user_id')
        return self.queryset.get(user__id=user_id) 
class ProviderUpdateView(APIView):
    def post(self, request):
        customer_id = request.data.get('user_id')
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({'error': 'Invalid customer ID'}, status=400)
        provider = Provider.objects.filter(user=customer).first()
        provider.provider_name = request.data.get('provider_name')
        provider.facebook = request.data.get('provider_facebook')
        provider.provider_email = request.data.get('provider_email')
        provider.provider_telephone = request.data.get('provider_telephone')
        provider.about = request.data.get('about')
        avatar_file = request.FILES.get('profile-photo-upload')
        if avatar_file:
            avatar_filename = f"{provider.id}_avatar.{avatar_file.name.split('.')[-1]}"
            provider.avatar.save(avatar_filename, avatar_file, save=True)
        cover_file = request.FILES.get('cover-photo-upload')
        if cover_file:
            cover_filename = f"{provider.id}_cover.{cover_file.name.split('.')[-1]}"
            provider.cover.save(cover_filename, cover_file, save=True)
        provider.save()    
        return redirect('http://localhost:3000/MyStore')    
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class =MyTokenObtainPairSerializer

@api_view(['GET'])
def getRoutes(request):
    routes =[
        'api/token',
        'api/token/refresh',
    ]
    return Response(routes)
# API 
class UserList(generics.ListAPIView):
    queryset= Customer.objects.all()
    serializer_class= CustomerSerializer
class ProviderList(generics.ListAPIView):
    queryset= Provider.objects.all()
    serializer_class= ProviderSerializer

class ProductCategoryList(APIView):
    def get(self, request):
        productCategory = ProductCategory.objects.all()
        serializer = ProductCategorySerializer(productCategory, many=True)
        return Response(serializer.data)    
class ProductAllList(generics.ListAPIView):
    tz = timezone('Asia/Bangkok')
    current_time = datetime.datetime.now(tz)
    # Query and delete records where the delete_at value is less than the current time
    expired_discount_products = DiscountProduct.objects.filter(delete_at__lte=current_time)
    queryset= Product.objects.all()
    serializer_class= AllProductSerializer

class ProductDetail(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = AllProductSerializer
    tz = timezone('Asia/Bangkok')
    current_time = datetime.datetime.now(tz)

    def dispatch(self, request, *args, **kwargs):
        # Query and delete records where the delete_at value is less than the current time
        expired_discount_products = DiscountProduct.objects.filter(delete_at__lte=self.current_time)
        if expired_discount_products.exists():
            expired_discount_products.delete()
        
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        pk = self.kwargs.get('pk')
        return queryset.filter(pk=pk)
class DiscountProductList(generics.ListAPIView):
    queryset= DiscountProduct.objects.all()
    serializer_class=DiscountProductSerializer
    
    
class AddToCartAPIView(APIView):
    def post(self, request):
        try:
            # Get the user/customer from the request data
            customer_id = request.data.get('customer_id')

            # Get the product_id, quantity, and any other relevant data from the request data
            product_id = request.data.get('product_id')
            quantity = int(request.data.get('quantity'))
            price = int(request.data.get('price'))
            color = request.data.get('color')
            size = request.data.get('size')
   
            # Validate the data (you can add more validation if needed)
            if not customer_id or not product_id or not quantity:
                return Response({"message": "Invalid input data."}, status=status.HTTP_400_BAD_REQUEST)

            product_attribute =ProductAttribute.objects.filter(color=color, size=size).first()
            product = Product.objects.get(id=product_id)
            discount_product =DiscountProduct.objects.filter(product_id=product_id).first()
            shopping_session = ShoppingSession.objects.filter(customer_id=customer_id).first()
            cart_item = Cart_items.objects.filter(session=shopping_session,
                product=product,
                product_attribute=product_attribute).first()    
 
            if not cart_item:
                cart_item = Cart_items.objects.create(
                    session=shopping_session,
                    product=product,
                    quantity=quantity,
                    product_attribute=product_attribute,
                )
            else:
                cart_item.quantity= cart_item.quantity +int(quantity)  
            if discount_product:
                discount =Discount.objects.get(id=discount_product.discount_id)
                shopping_session.total = shopping_session.total + product.price * discount.discount_percent* cart_item.quantity
            else:
                shopping_session.total = shopping_session.total + product.price * cart_item.quantity
            shopping_session.total = round(shopping_session.total/1000)*1000     
            shopping_session.save()         
            cart_item.save()
            return Response({"message": "Item added to the cart successfully."}, status=status.HTTP_201_CREATED)

        except Customer.DoesNotExist:
            logging.error("Customer not found.")
            return Response({"message": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)

        except Product.DoesNotExist:
            logging.error("Product not found.")
            return Response({"message": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logging.exception("An error occurred:")
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class RemoveCartItemView(APIView):
    def post(self, request, cart_item_id):
        try:
            cart_item = Cart_items.objects.get(id=cart_item_id)
            shopping_session = ShoppingSession.objects.get(id=cart_item.session_id)
            discount_product =DiscountProduct.objects.filter(product_id=cart_item.product_id).first()
            
            product = Product.objects.get(id=cart_item.product_id)
            if discount_product:
                discount =Discount.objects.get(id=discount_product.discount_id)
                shopping_session.total = shopping_session.total - product.price * discount.discount_percent* cart_item.quantity
            else:
                shopping_session.total = shopping_session.total - product.price * cart_item.quantity
            shopping_session.total = round(shopping_session.total/1000)*1000    
            shopping_session.save()  # Save the updated total to the shopping session
            cart_item.delete()
            return Response({'message': 'Cart item removed successfully'}, status=status.HTTP_200_OK)
        except Cart_items.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # Logging other exceptions
            logging.exception("An error occurred")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class ShoppingSessionView(APIView):
    current_time = datetime.datetime.now()
    def dispatch(self, request, *args, **kwargs):
        expired_discount_products = DiscountProduct.objects.filter(delete_at__lte=self.current_time)
        if expired_discount_products.exists():
            for expired_product in expired_discount_products:
                cart_item = Cart_items.objects.filter(product=expired_product.product)
                if cart_item.exists():
                    shopping_session = ShoppingSession.objects.get(id=cart_item[0].session_id)
                    if expired_product.discount:
                        shopping_session.total = shopping_session.total + expired_product.product.price * expired_product.discount.discount_percent * cart_item[0].quantity
                    else:
                        shopping_session.total = shopping_session.total + expired_product.product.price * cart_item[0].quantity
                    shopping_session.save()

                expired_product.delete()

        return super().dispatch(request, *args, **kwargs)
    def get(self, request,customer_id):
        try:
            

            customer = Customer.objects.get(id=customer_id)
            shopping_session = ShoppingSession.objects.filter(customer=customer).first()

            if shopping_session:
                serializer = ShoppingSessionSerializer(shopping_session)
                return Response(serializer.data)
            else:
                return Response({"error": "Shopping session not found for this customer."},
                                status=status.HTTP_404_NOT_FOUND)

        except Customer.DoesNotExist:
            logging.error("Customer not found.")
            return Response({"error": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)
        