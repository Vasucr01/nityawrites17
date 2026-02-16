from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.core.management import call_command
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Book, Order, OrderItem, Payment, AboutSection, SocialMedia
import uuid
from urllib.parse import quote


def home(request):
    """Display all books on the homepage"""
    books = Book.objects.filter(stock__gt=0)
    about = AboutSection.objects.filter(is_active=True).first()
    social_links = SocialMedia.objects.filter(is_active=True)
    
    return render(request, 'store/index.html', {
        'books': books,
        'about': about,
        'social_links': social_links
    })


def book_detail(request, pk):
    """Display detailed view of a single book"""
    book = get_object_or_404(Book, pk=pk)
    social_links = SocialMedia.objects.filter(is_active=True)
    return render(request, 'store/book_detail.html', {
        'book': book,
        'social_links': social_links
    })


def cart_add(request, pk):
    """Add a book to the cart"""
    book = get_object_or_404(Book, pk=pk)
    cart = request.session.get('cart', {})
    
    book_id = str(pk)
    if book_id in cart:
        cart[book_id]['quantity'] += 1
    else:
        cart[book_id] = {
            'title': book.title,
            'price': str(book.price),
            'quantity': 1,
            'image': book.image.url if book.image else ''
        }
    
    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart_detail')


def cart_detail(request):
    """Display cart contents"""
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    
    for book_id, item in cart.items():
        item_total = float(item['price']) * item['quantity']
        cart_items.append({
            'id': book_id,
            'title': item['title'],
            'price': item['price'],
            'quantity': item['quantity'],
            'total': item_total,
            'image': item['image']
        })
        total += item_total
    
    social_links = SocialMedia.objects.filter(is_active=True)
    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total': total,
        'social_links': social_links
    })


def cart_update(request, pk):
    """Update quantity of an item in cart"""
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        book_id = str(pk)
        quantity = int(request.POST.get('quantity', 1))
        
        if book_id in cart:
            if quantity > 0:
                cart[book_id]['quantity'] = quantity
            else:
                del cart[book_id]
        
        request.session['cart'] = cart
        request.session.modified = True
    
    return redirect('cart_detail')


def cart_remove(request, pk):
    """Remove an item from cart"""
    cart = request.session.get('cart', {})
    book_id = str(pk)
    
    if book_id in cart:
        del cart[book_id]
    
    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart_detail')


def checkout(request):
    """Display checkout form"""
    cart = request.session.get('cart', {})
    
    if not cart:
        return redirect('home')
    
    cart_items = []
    total = 0
    
    for book_id, item in cart.items():
        item_total = float(item['price']) * item['quantity']
        cart_items.append({
            'id': book_id,
            'title': item['title'],
            'price': item['price'],
            'quantity': item['quantity'],
            'total': item_total
        })
        total += item_total
    
    return render(request, 'store/checkout.html', {
        'cart_items': cart_items,
        'total': total
    })


def payment_process(request):
    """Process payment using UPI QR code"""
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        
        if not cart:
            return redirect('home')
        
        # Calculate total
        total = sum(float(item['price']) * item['quantity'] for item in cart.values())
        
        # Create order
        order_id = f"ORD{uuid.uuid4().hex[:8].upper()}"
        order = Order.objects.create(
            order_id=order_id,
            customer_name=request.POST.get('name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            address_line1=request.POST.get('address1'),
            address_line2=request.POST.get('address2', ''),
            city=request.POST.get('city'),
            state=request.POST.get('state'),
            pincode=request.POST.get('pincode'),
            country=request.POST.get('country', 'India'),
            total_amount=total,
            payment_status='pending'
        )
        
        # Create order items
        for book_id, item in cart.items():
            book = Book.objects.get(pk=int(book_id))
            OrderItem.objects.create(
                order=order,
                book=book,
                quantity=item['quantity'],
                price=item['price']
            )
        
        # Create payment record
        Payment.objects.create(
            order=order,
            amount=total,
            status='pending'
        )
        
        # Store order ID in session
        request.session['current_order_id'] = order.id
        
        # Simple context for manual payment
        upi_id = settings.UPI_ID
        payee_name = 'Nitya'
        amount_formatted = "{:.2f}".format(total)
        
        # UPI string for QR code
        upi_string = f"upi://pay?pa={upi_id}&pn={payee_name}&am={amount_formatted}&cu=INR"
        
        # Generate QR code
        import qrcode
        import io
        import base64
        
        qr_img = qrcode.make(upi_string)
        buffer = io.BytesIO()
        qr_img.save(buffer, format='PNG')
        buffer.seek(0)
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        context = {
            'order': order,
            'total': total,
            'upi_id_debug': upi_id,
            'qr_code': qr_code_base64,
            'upi_link': upi_string
        }
        
        return render(request, 'store/payment.html', context)
    
    return redirect('checkout')


def upload_payment_proof(request, order_id):
    """Handle payment screenshot upload"""
    if request.method == 'POST':
        try:
            order = Order.objects.get(pk=order_id)
            payment = order.payment
            
            # Save payment reference if provided
            payment_ref = request.POST.get('payment_reference', '').strip()
            if payment_ref:
                payment.payment_reference = payment_ref
            
            # Save screenshot
            if 'payment_screenshot' in request.FILES:
                payment.payment_screenshot = request.FILES['payment_screenshot']
                payment.status = 'pending_verification'
                payment.save()
                
                # Update order status
                order.payment_status = 'pending_verification'
                order.save()
                
                return render(request, 'store/payment_submitted.html', {'order': order})
            else:
                return render(request, 'store/payment.html', {
                    'order': order,
                    'error': 'Please upload a payment screenshot',
                    'total': order.total_amount,
                    'upi_id_debug': settings.UPI_ID
                })
        except Order.DoesNotExist:
            return redirect('home')
    
    return redirect('home')


@csrf_exempt
def payment_callback(request):
    """Handle UPI payment confirmation with transaction ID"""
    if request.method == 'POST':
        upi_transaction_id = request.POST.get('upi_transaction_id')
        
        # Get order from session
        order_pk = request.session.get('current_order_id')
        order = Order.objects.get(pk=order_pk)
        
        # Update payment
        payment = Payment.objects.get(order=order)
        payment.upi_transaction_id = upi_transaction_id
        payment.status = 'completed'
        payment.save()
        
        # Update order status
        order.payment_status = 'completed'
        order.save()
        
        # Update stock
        for item in order.items.all():
            book = item.book
            book.stock -= item.quantity
            book.save()
        
        # Send confirmation email
        send_order_confirmation_email(order)
        
        # Clear cart
        request.session['cart'] = {}
        request.session.modified = True
        
        return redirect('order_success', order_id=order.order_id)
    
    return redirect('home')


def send_order_confirmation_email(order):
    """Send order confirmation email to customer"""
    try:
        # Prepare email content
        subject = f'Order Confirmation - Nityawrites.com 📚 (Order #{order.order_id})'
        
        # Get order items
        items_list = []
        for item in order.items.all():
            items_list.append(f"{item.book.title} x {item.quantity} - ₹{item.price}")
        
        # Create email body
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #7a5c4d; text-align: center;">Thank You for Your Order! 📚</h2>
                
                <p>Dear {order.customer_name},</p>
                
                <p>We're delighted to confirm your order from <strong>Nityawrites</strong>!</p>
                
                <div style="background: #f9f9f9; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #7a5c4d; margin-top: 0;">Order Details</h3>
                    <p><strong>Order ID:</strong> {order.order_id}</p>
                    <p><strong>Order Date:</strong> {order.created_at.strftime('%B %d, %Y at %I:%M %p')}</p>
                    <p><strong>UPI Transaction ID:</strong> {order.payment.upi_transaction_id}</p>
                </div>
                
                <div style="background: #f9f9f9; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #7a5c4d; margin-top: 0;">Books Ordered</h3>
                    <ul style="list-style: none; padding: 0;">
                        {''.join([f'<li style="padding: 5px 0; border-bottom: 1px solid #ddd;">{item}</li>' for item in items_list])}
                    </ul>
                    <p style="font-size: 18px; font-weight: bold; margin-top: 15px;">Total Amount: ₹{order.total_amount}</p>
                </div>
                
                <div style="background: #f9f9f9; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #7a5c4d; margin-top: 0;">Delivery Address</h3>
                    <p>
                        {order.customer_name}<br>
                        {order.address_line1}<br>
                        {order.address_line2 + '<br>' if order.address_line2 else ''}
                        {order.city}, {order.state} - {order.pincode}<br>
                        {order.country}<br>
                        <strong>Phone:</strong> {order.phone}
                    </p>
                </div>
                
                <div style="background: #7a5c4d; color: white; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
                    <p style="margin: 0; font-size: 16px;">
                        <strong>Thank you for ordering from Nityawrites.</strong><br>
                        Your support means the world to independent authors.<br>
                        Happy Reading 📖✨
                    </p>
                </div>
                
                <p style="text-align: center; color: #666; font-size: 12px; margin-top: 30px;">
                    © 2026 Nityawrites. All rights reserved.
                </p>
            </div>
        </body>
        </html>
        """
        
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error sending email: {e}")


def order_success(request, order_id):
    """Display order success page"""
    order = get_object_or_404(Order, order_id=order_id)
    return render(request, 'store/order_success.html', {'order': order})



def order_failed(request):
    """Display order failure page"""
    return render(request, 'store/order_failed.html')


def force_migrate(request):
    """Temporary view to run migrations manually in production and force-add columns"""
    import io
    from django.db import connection
    output = io.StringIO()
    try:
        # 1. Try standard migration
        call_command('migrate', interactive=False, stdout=output)
        
        # 2. Force add columns using raw SQL in case migration record is out of sync
        with connection.cursor() as cursor:
            try:
                # Add columns if they don't exist
                cursor.execute('ALTER TABLE store_payment ADD COLUMN IF NOT EXISTS payment_reference VARCHAR(200);')
                cursor.execute('ALTER TABLE store_payment ADD COLUMN IF NOT EXISTS payment_screenshot VARCHAR(100);')
                cursor.execute('ALTER TABLE store_payment ADD COLUMN IF NOT EXISTS verified_at TIMESTAMP WITH TIME ZONE;')
                output.write("\nRaw SQL column additions attempted (IF NOT EXISTS).")
            except Exception as sql_e:
                output.write(f"\nRaw SQL failed: {str(sql_e)}")
                
        return HttpResponse(f"Migration tool finished.<br><pre>{output.getvalue()}</pre>")
    except Exception as e:
        return HttpResponse(f"Migration tool fatal error: {str(e)}", status=500)


def admin_order_verify(request, pk):
    """Quick verify view for admin"""
    if not request.user.is_staff:
        return HttpResponse("Unauthorized", status=403)
    
    from django.utils import timezone
    order = get_object_or_404(Order, pk=pk)
    order.payment_status = 'verified'
    order.save()
    
    # Update payment
    payment = getattr(order, 'payment', None)
    if payment:
        payment.status = 'verified'
        payment.verified_at = timezone.now()
        payment.save()
        
    # Send email
    try:
        send_order_confirmation_email(order)
    except Exception as e:
        print(f"Error sending email: {e}")
        
    return redirect('/admin/store/order/')


def admin_order_fail(request, pk):
    """Quick fail view for admin"""
    if not request.user.is_staff:
        return HttpResponse("Unauthorized", status=403)
    
    order = get_object_or_404(Order, pk=pk)
    order.payment_status = 'failed'
    order.save()
    
    # Update payment
    payment = getattr(order, 'payment', None)
    if payment:
        payment.status = 'failed'
        payment.save()
        
    return redirect('/admin/store/order/')
def test_email_view(request):
    """View to test if SMTP is working"""
    if not request.user.is_staff:
        return HttpResponse("Unauthorized", status=403)
    
    test_email = request.GET.get('email', settings.EMAIL_HOST_USER)
    try:
        send_mail(
            'Test Email from Nityawrites',
            'If you are reading this, your SMTP settings are working correctly! 📚✨',
            settings.DEFAULT_FROM_EMAIL,
            [test_email],
            fail_silently=False,
        )
        return HttpResponse(f"Test email successfully sent to {test_email}!")
    except Exception as e:
        import traceback
        return HttpResponse(f"FAILED to send test email: {str(e)}<br><pre>{traceback.format_exc()}</pre>")
