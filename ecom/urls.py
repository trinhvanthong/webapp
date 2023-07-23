from django.urls import path 
from . import views

from .views import MyTokenObtainPairView, RegisterView,registration_confirm, ProviderRegisterView,ProviderDetailView, ProviderUpdateView,AddProduct,AddToCartAPIView,ShoppingSessionView,RemoveCartItemView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
urlpatterns = [
    path('',views.getRoutes),
    path('register/', RegisterView.as_view(), name='register'),
    path('providers/<int:user_id>/', ProviderDetailView.as_view(), name='provider-detail'),
    path('providerRegister/', ProviderRegisterView.as_view(), name='provider-register'),
    path('providerUpdate/', ProviderUpdateView.as_view(), name='provider-update'),
    path('addProduct/', AddProduct.as_view(), name='add-product'),
    path('registration/confirm/', registration_confirm, name='registration-confirm'),
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('providerAPI/', views.ProviderList.as_view(), name='provider-list'),
    path('providerAPI111/', views.DiscountProductList.as_view(), name='provider11-list'),
    path('userAPI/', views.UserList.as_view(), name='user-list'),
    path('productCategoryAPI/', views.ProductCategoryList.as_view(), name='product-category-list'),
    path('productAPI/', views.ProductAllList.as_view(), name='product-list'),
    path('productAPI/<int:pk>', views.ProductDetail.as_view(), name='product-detail'),
    path('api/add_to_cart/', AddToCartAPIView.as_view(), name='api_add_to_cart'),
    path('api/shopping_session/<int:customer_id>/', ShoppingSessionView.as_view(), name='shopping_session'),
    path('removeCartItem/<int:cart_item_id>/', RemoveCartItemView.as_view(), name='remove_cart_item'),
]
