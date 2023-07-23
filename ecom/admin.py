from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(ProductCategory)
admin.site.register(ProductImage)
admin.site.register(ProductAttribute)
admin.site.register(Category)
admin.site.register(ProductInventory)
admin.site.register(Discount)
admin.site.register(Product)
admin.site.register(PaymentDetails)
admin.site.register(OrderDetails)
admin.site.register(OrderItems)
admin.site.register(Customer)
admin.site.register(CustomerAddress)
admin.site.register(Provider)
admin.site.register(ProviderAddress)
admin.site.register(DiscountProduct)
admin.site.register(ShoppingSession)
admin.site.register(Cart_items)

