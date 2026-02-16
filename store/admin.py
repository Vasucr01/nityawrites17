from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
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
    list_display = ['order_id', 'customer_name', 'phone', 'total_amount', 'payment_status', 'quick_actions', 'created_at']
    list_filter = ['payment_status', 'created_at']
    search_fields = ['order_id', 'customer_name', 'email', 'phone']
    readonly_fields = ['order_id', 'created_at', 'quick_actions']
    list_editable = ['payment_status']
    inlines = [OrderItemInline]
    actions = [export_orders_to_excel, 'mark_as_verified', 'mark_as_failed']

    def quick_actions(self, obj):
        from django.utils.safestring import mark_safe
        verify_url = f"/manage-order/verify/{obj.pk}/"
        fail_url = f"/manage-order/fail/{obj.pk}/"
        return mark_safe(f"""
            <a class="button" href="{verify_url}" style="background: #28a745; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none; margin-right: 5px; font-size: 11px;">✅ Verify</a>
            <a class="button" href="{fail_url}" style="background: #dc3545; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none; font-size: 11px;">❌ Fail</a>
        """)
    quick_actions.short_description = 'Quick Actions'

    def mark_as_verified(self, request, queryset):
        from .views import send_order_confirmation_email
        from django.utils import timezone
        count = 0
        for order in queryset:
            order.payment_status = 'verified'
            order.save()
            # Update associated payment
            payment = getattr(order, 'payment', None)
            if payment:
                payment.status = 'verified'
                payment.verified_at = timezone.now()
                payment.save()
            
            # Send email
            try:
                send_order_confirmation_email(order)
            except Exception as e:
                self.message_user(request, f"Error sending email for {order.order_id}: {e}", level='Warning')
            
            count += 1
        self.message_user(request, f'{count} order(s) marked as verified and emails sent.')
    mark_as_verified.short_description = "✅ Mark as Verified & Send Email"

    def mark_as_failed(self, request, queryset):
        count = queryset.update(payment_status='failed')
        for order in queryset:
            payment = getattr(order, 'payment', None)
            if payment:
                payment.status = 'failed'
                payment.save()
        self.message_user(request, f'{count} order(s) marked as failed.')
    mark_as_failed.short_description = "❌ Mark as Failed"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'book', 'quantity', 'price']
    list_filter = ['order']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'payment_reference', 'amount', 'status', 'quick_actions', 'created_at', 'has_screenshot']
    list_filter = ['status', 'created_at']
    search_fields = ['upi_transaction_id', 'payment_reference', 'order__order_id']
    readonly_fields = ['created_at', 'screenshot_preview', 'quick_actions']
    list_editable = ['status']
    fields = ['order', 'upi_transaction_id', 'payment_reference', 'amount', 'status', 'created_at', 'verified_at', 'screenshot_preview', 'payment_screenshot']
    actions = ['mark_as_verified', 'mark_as_failed']
    
    def has_screenshot(self, obj):
        """Show if payment has screenshot"""
        return bool(obj.payment_screenshot)
    has_screenshot.boolean = True
    has_screenshot.short_description = 'Screenshot'
    
    def screenshot_preview(self, obj):
        """Display screenshot preview in admin"""
        if obj.payment_screenshot:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="max-width: 300px; max-height: 300px; border: 2px solid #ddd; border-radius: 5px;"/></a>',
                obj.payment_screenshot.url,
                obj.payment_screenshot.url
            )
        return "No screenshot uploaded"
    screenshot_preview.short_description = 'Payment Screenshot'
    
    def quick_actions(self, obj):
        from django.utils.safestring import mark_safe
        verify_url = f"/manage-order/verify/{obj.order.pk}/"
        fail_url = f"/manage-order/fail/{obj.order.pk}/"
        return mark_safe(f"""
            <a class="button" href="{verify_url}" style="background: #28a745; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none; margin-right: 5px; font-size: 11px;">✅ Verify</a>
            <a class="button" href="{fail_url}" style="background: #dc3545; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none; font-size: 11px;">❌ Fail</a>
        """)
    quick_actions.short_description = 'Quick Actions'

    def mark_as_verified(self, request, queryset):
        """Mark selected payments as verified"""
        from .views import send_order_confirmation_email
        from django.utils import timezone
        count = 0
        for payment in queryset:
            payment.status = 'verified'
            payment.verified_at = timezone.now()
            payment.save()
            # Update order status
            payment.order.payment_status = 'verified'
            payment.order.save()
            
            # Send email
            try:
                send_order_confirmation_email(payment.order)
            except Exception as e:
                self.message_user(request, f"Error sending email for {payment.order.order_id}: {e}", level='Warning')
                
            count += 1
        self.message_user(request, f'{count} payment(s) marked as verified and emails sent.')
    mark_as_verified.short_description = "✅ Mark as Verified & Send Email"
    
    def mark_as_failed(self, request, queryset):
        """Mark selected payments as failed"""
        count = queryset.update(status='failed')
        for payment in queryset:
            payment.order.payment_status = 'failed'
            payment.order.save()
        self.message_user(request, f'{count} payment(s) marked as failed.')
    mark_as_failed.short_description = "❌ Mark as Failed"


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
