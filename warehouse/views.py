from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.db.models.functions import ExtractMonth
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from .models import Category, Product, Supplier, Order, OrderItem, Inventory
from .forms import CategoryForm, ProductForm, SupplierForm, OrderForm, OrderItemForm, InventoryForm
import json
import csv
from datetime import datetime

@login_required
def dashboard(request):
    if request.method == 'POST':
        if 'export_data' in request.POST:
            # Export all data
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="warehouse_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['Category', 'Total Products', 'Low Stock Products'])
            
            categories = Category.objects.annotate(
                total_products=Count('products'),
                low_stock=Count('products', filter=Q(products__quantity__lte=10))
            )
            
            for category in categories:
                writer.writerow([
                    category.name,
                    category.total_products,
                    category.low_stock
                ])
            
            return response
            
        elif 'export_monthly_orders' in request.POST:
            # Export monthly orders data
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="monthly_orders_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['Month', 'Total Orders'])
            
            # Get monthly order counts using ExtractMonth
            monthly_orders = Order.objects.annotate(
                month=ExtractMonth('created_at')
            ).values('month').annotate(
                total_orders=Count('id')
            ).order_by('month')
            
            months = ['January', 'February', 'March', 'April', 'May', 'June', 
                     'July', 'August', 'September', 'October', 'November', 'December']
            
            for order in monthly_orders:
                month_num = order['month']
                writer.writerow([
                    months[month_num-1],
                    order['total_orders']
                ])
            
            return response
            
        elif 'export_category_data' in request.POST:
            # Export category data
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="category_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['Category', 'Total Products'])
            
            categories = Category.objects.annotate(product_count=Count('products'))
            
            for category in categories:
                writer.writerow([
                    category.name,
                    category.product_count
                ])
            
            return response
            
        elif 'export_order_status' in request.POST:
            # Export order status data
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="order_status_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['Status', 'Count'])
            
            order_status = Order.objects.values('status').annotate(count=Count('id'))
            
            for status in order_status:
                writer.writerow([
                    status['status'],
                    status['count']
                ])
            
            return response
            
        elif 'new_order' in request.POST:
            # Create new order
            return redirect('warehouse:order_list')
    
    total_products = Product.objects.count()
    total_suppliers = Supplier.objects.count()
    total_orders = Order.objects.count()
    low_stock_products = Product.objects.filter(quantity__lte=10)
    recent_orders = Order.objects.order_by('-created_at')[:5]
    
    # Category Chart Data
    categories = Category.objects.annotate(product_count=Count('products'))
    category_labels = json.dumps([cat.name for cat in categories])
    category_data = json.dumps([cat.product_count for cat in categories])
    
    # Order Status Chart Data
    order_status = Order.objects.values('status').annotate(count=Count('id'))
    order_status_labels = json.dumps([status['status'] for status in order_status])
    order_status_data = json.dumps([status['count'] for status in order_status])
    
    # Monthly Orders Data using ExtractMonth
    monthly_orders = Order.objects.annotate(
        month=ExtractMonth('created_at')
    ).values('month').annotate(
        total_orders=Count('id')
    ).order_by('month')

    monthly_data = [0] * 12
    for order in monthly_orders:
        month_num = order['month'] - 1  # 0-based index for array
        monthly_data[month_num] = order['total_orders']
    
    context = {
        'total_products': total_products,
        'total_suppliers': total_suppliers,
        'total_orders': total_orders,
        'low_stock_products': low_stock_products,
        'recent_orders': recent_orders,
        'category_labels': category_labels,
        'category_data': category_data,
        'order_status_labels': order_status_labels,
        'order_status_data': order_status_data,
        'monthly_orders_data': json.dumps(monthly_data)
    }
    return render(request, 'warehouse/dashboard.html', context)

@login_required
def product_list(request):
    products = Product.objects.all().select_related('category').order_by('-created_at')
    
    if request.method == 'POST':
        if 'add_product' in request.POST:
            form = ProductForm(request.POST)
            if form.is_valid():
                product = form.save()
                messages.success(request, 'Product added successfully!')
                return redirect('warehouse:product_list')
            else:
                messages.error(request, 'Please correct the errors below.')
        elif 'edit_product' in request.POST:
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, pk=product_id)
            form = ProductForm(request.POST, instance=product)
            if form.is_valid():
                form.save()
                messages.success(request, 'Product updated successfully!')
                return redirect('warehouse:product_list')
            else:
                messages.error(request, 'Please correct the errors below.')
        elif 'delete_product' in request.POST:
            product_id = request.POST.get('product_id')
            try:
                product = Product.objects.get(pk=product_id)
                name = product.name
                product.delete()
                messages.success(request, f'Product "{name}" deleted successfully!')
            except Product.DoesNotExist:
                messages.error(request, 'Product not found.')
            except Exception as e:
                messages.error(request, f'Error deleting product: {str(e)}')
            return redirect('warehouse:product_list')
    
    # Create a dictionary of forms for each product
    product_forms = {product.id: ProductForm(instance=product) for product in products}
    add_form = ProductForm()
    
    return render(request, 'warehouse/product_list.html', {
        'products': products,
        'form': add_form,
        'product_forms': product_forms,
    })

@login_required
def product_delete(request, pk):
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, pk=pk)
            name = product.name
            product.delete()
            messages.success(request, f'Product "{name}" deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting product: {str(e)}')
    return redirect('warehouse:product_list')

@login_required
def supplier_list(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier added successfully!')
            return redirect('warehouse:supplier_list')
    else:
        form = SupplierForm()
    
    suppliers = Supplier.objects.all()
    return render(request, 'warehouse/supplier_list.html', {
        'suppliers': suppliers,
        'form': form
    })

@login_required
def order_list(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.created_by = request.user
            order.save()
            messages.success(request, 'Order created successfully!')
            return redirect('warehouse:order_list')
    else:
        form = OrderForm()
    
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'warehouse/order_list.html', {
        'orders': orders,
        'form': form
    })

@login_required
def inventory_list(request):
    if request.method == 'POST':
        form = InventoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Inventory record added successfully!')
            return redirect('warehouse:inventory_list')
    else:
        form = InventoryForm()
    
    inventory = Inventory.objects.all()
    return render(request, 'warehouse/inventory_list.html', {
        'inventory': inventory,
        'form': form
    })

@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    inventory = Inventory.objects.filter(product=product)
    
    if request.method == 'POST':
        if 'delete' in request.POST:
            try:
                name = product.name
                product.delete()
                messages.success(request, f'Product "{name}" deleted successfully!')
                return redirect('warehouse:product_list')
            except Exception as e:
                messages.error(request, f'Error deleting product: {str(e)}')
        else:
            form = ProductForm(request.POST, instance=product)
            if form.is_valid():
                form.save()
                messages.success(request, 'Product updated successfully!')
                return redirect('warehouse:product_detail', pk=pk)
            else:
                messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'warehouse/product_detail.html', {
        'product': product,
        'inventory': inventory,
        'form': form
    })
