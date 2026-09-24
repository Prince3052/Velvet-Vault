from django.contrib import admin
from .models import *
from checkout.models import Order
# Register your models here.

class ProductVideoInline(admin.TabularInline):
    model = ProductVideo
    extra = 1

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(JewelryItem)
class JewelryItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'is_active')
    search_fields = ('name', 'sku')
    inlines = [ProductImageInline, ProductVideoInline]

admin.site.register(TeamMember)

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    search_fields = ('name',)

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'is_published')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'amount', 'payment_method', 'is_paid', 'created_at')
    list_filter = ('payment_method', 'is_paid', 'created_at')
    search_fields = ('user__username', 'product__name')


# @admin.register(Payment)
# class PaymentAdmin(admin.ModelAdmin):
#     list_display = ('id', 'user', 'product', 'amount', 'status', 'created_at')
#     list_filter = ('status',)