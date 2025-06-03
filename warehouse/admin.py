from django.contrib import admin
from .models import Category, Product, Supplier, Order, OrderItem, Inventory

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'sku', 'quantity', 'unit_price')
    list_filter = ('category',)
    search_fields = ('name', 'sku')

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'email', 'phone')
    search_fields = ('name', 'contact_person')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'supplier', 'status', 'created_by', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'supplier__name')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'unit_price')
    list_filter = ('order', 'product')

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'location', 'last_updated')
    list_filter = ('location',)
    search_fields = ('product__name', 'location')
