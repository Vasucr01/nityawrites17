from django.contrib import admin
from django.http import HttpResponse
from openpyxl import Workbook
from .models import Book, Order, OrderItem, Payment, AboutSection, SocialMedia


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'price', 'stock', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'author']
    list_editable = ['price', 'stock']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['book', 'quantity', 'price']


def export_orders_to_excel(modeladmin, request, queryset):
    """Export selected orders to Excel"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Orders"
    
    # Headers
    headers = ['Order ID', 'Customer Name', 'Phone', 'Email', 'Address', 'City', 
               'State', 'Pincode', 'Books', 'Quantity', 'Total Amount', 
               'Payment Status', 'Date']
    ws.append(headers)
    
    # Data
    for order in queryset:
        items = order.items.all()
        books_str = ', '.join([f"{item.book.title} (x{item.quantity})" for item in items])
        total_qty = sum([item.quantity for item in items])
        
        full_address = f"{order.address_line1}, {order.address_line2}, {order.city}, {order.state} - {order.pincode}"
        
        row = [
            order.order_id,
            order.customer_name,
            order.phone,
            order.email,
            full_address,
            order.city,
            order.state,
            order.pincode,
            books_str,
            total_qty,
            float(order.total_amount),
            order.payment_status,
            order.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ]
        ws.append(row)
    
    # Create response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=orders.xlsx'
    wb.save(response)
    return response

export_orders_to_excel.short_description = "Export to Excel"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'customer_name', 'phone', 'total_amount', 'payment_status', 'created_at']
    list_filter = ['payment_status', 'created_at']
    search_fields = ['order_id', 'customer_name', 'email', 'phone']
    readonly_fields = ['order_id', 'created_at']
    inlines = [OrderItemInline]
    actions = [export_orders_to_excel]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'book', 'quantity', 'price']
    list_filter = ['order']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'upi_transaction_id', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['upi_transaction_id']
    readonly_fields = ['created_at']


@admin.register(AboutSection)
class AboutSectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'updated_at']
    list_filter = ['is_active']
    fields = ['title', 'description', 'author_image', 'is_active']
    
    def save_model(self, request, obj, form, change):
        # Ensure only one active About section
        if obj.is_active:
            AboutSection.objects.exclude(pk=obj.pk).update(is_active=False)
        super().save_model(request, obj, form, change)


@admin.register(SocialMedia)
class SocialMediaAdmin(admin.ModelAdmin):
    list_display = ['platform', 'url', 'is_active', 'order']
    list_filter = ['platform', 'is_active']
    list_editable = ['is_active', 'order']
