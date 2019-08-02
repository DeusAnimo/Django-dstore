from django.contrib import admin

from .models import Order, OrderItem, Item, Category

admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Category)

