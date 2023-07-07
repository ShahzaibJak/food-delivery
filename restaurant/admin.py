from django.contrib import admin

# Register your models here.
from .models import Menu,Cart,CartItem,Order,OrderItem,Booking


admin.site.register(Menu)
admin.site.register(Booking)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)

