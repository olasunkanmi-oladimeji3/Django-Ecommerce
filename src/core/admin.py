from django.contrib import admin
from core.models import Item,OrderItem,Order,Category,BillingAddress,Payment
# Register your models here.

admin.site.register(Category)
admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(BillingAddress)
admin.site.register(Payment)
