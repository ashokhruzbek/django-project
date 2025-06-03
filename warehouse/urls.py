from django.urls import path
from . import views

app_name = 'warehouse'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('orders/', views.order_list, name='order_list'),
    path('inventory/', views.inventory_list, name='inventory_list'),
] 