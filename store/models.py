from django.db import models
from django.utils import timezone

class Book(models.Model):
    """Model for books available in the store"""
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100, default='Nitya')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='books/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']


class Order(models.Model):
    """Model for customer orders"""
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    order_id = models.CharField(max_length=100, unique=True)
    customer_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    country = models.CharField(max_length=100, default='India')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Order {self.order_id} - {self.customer_name}"
    
    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    """Model for items in an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} x {self.book.title}"
    
    def get_total(self):
        return self.quantity * self.price


class Payment(models.Model):
    """Model for payment transactions"""
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    upi_transaction_id = models.CharField(max_length=200, blank=True, help_text='UPI Transaction/Reference ID')
    payment_reference = models.CharField(max_length=200, blank=True, help_text='Customer entered payment reference number')
    payment_screenshot = models.ImageField(upload_to='payment_screenshots/', blank=True, null=True, help_text='Payment proof screenshot')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True, help_text='When payment was verified by admin')
    
    def __str__(self):
        return f"Payment for {self.order.order_id}"


class AboutSection(models.Model):
    """Model for About the Author section"""
    title = models.CharField(max_length=200, default='About Nityawrites')
    description = models.TextField(help_text='About the author or bookstore')
    author_image = models.ImageField(upload_to='about/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'About Section'
        verbose_name_plural = 'About Section'


class SocialMedia(models.Model):
    """Model for social media links"""
    PLATFORM_CHOICES = [
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('youtube', 'YouTube'),
    ]
    
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    url = models.URLField(help_text='Full URL to your social media profile')
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0, help_text='Display order')
    
    def __str__(self):
        return f"{self.get_platform_display()}"
    
    class Meta:
        verbose_name = 'Social Media Link'
        verbose_name_plural = 'Social Media Links'
        ordering = ['order']


class Review(models.Model):
    """Model for customer reviews on books"""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=100)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.name} on {self.book.title}"

    class Meta:
        ordering = ['-created_at']
