from django.contrib import admin
from django.db.models import Sum
from django.template.response import TemplateResponse
from django.urls import path
from .models import User, Category, Product, Cart, CartItem, Order, ElectronicNews, Review, OrderItem
# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    search_fields = ["name"]

class QLBanDodungAdminSite(admin.AdminSite):
    site_header = "QUẢN LÝ CỬA HÀNG VĂN PHÒNG PHẨM"

admin_site = QLBanDodungAdminSite(name='myAdmin')

admin_site.register(User)
admin_site.register(Category)
admin_site.register(Product, ProductAdmin)
admin_site.register(Cart)
admin_site.register(CartItem)
admin_site.register(Order)
admin_site.register(OrderItem)
admin_site.register(ElectronicNews)
admin_site.register(Review)

