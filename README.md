nityawrites.com - Django Online Bookstore

A fully functional Django-based online bookstore for selling books with UPI payment integration, email confirmations, and admin management.

## Features

- **Book Management**: Display books with images, prices, and descriptions
- **Shopping Cart**: Session-based cart (no login required)
- **Checkout System**: Complete customer and delivery information collection
- **UPI Payment**: Direct UPI deeplink integration (opens UPI apps)
- **Email Confirmations**: Automated order confirmation emails
- **About Section**: Admin-editable About the Author section
- **Social Media**: Instagram and other social media integration
- **Admin Panel**: Manage books, view orders, export to Excel
- **Order Tracking**: Complete order history with UPI transaction IDs

## Tech Stack

- **Backend**: Django 5.1.4
- **Database**: SQLite (easily upgradable to PostgreSQL)
- **Payment**: UPI Deeplink (nityabhambhani17@oksbi)
- **Email**: Django SMTP (Gmail)
- **Excel Export**: openpyxl
- **Image Handling**: Pillow

## Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Email Settings

Edit `nityawrites/settings.py` and add your Gmail credentials:

```python
EMAIL_HOST_USER = 'your_email@gmail.com'
EMAIL_HOST_PASSWORD = 'your_gmail_app_password'
DEFAULT_FROM_EMAIL = 'Nityawrites <your_email@gmail.com>'
```

**How to get Gmail App Password:**
1. Go to your Google Account settings
2. Security → 2-Step Verification → App passwords
3. Generate a new app password for "Mail"
4. Use that password in settings

### 3. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

### 5. Run Development Server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

## Usage

### Admin Panel

Access the admin panel at: http://127.0.0.1:8000/admin/

**Admin Features:**
- Add/Edit/Delete books
- Upload book cover images
- Update prices and stock
- View all orders with UPI transaction IDs
- Export orders to Excel
- Edit About Section
- Manage Social Media Links

### Setting Up About Section

1. Login to admin panel
2. Go to "About Section"
3. Click "Add About Section"
4. Fill in:
   - Title (e.g., "About Nityawrites")
   - Description (about the author)
   - Upload author image (optional)
   - Check "Is active"
5. Save

### Adding Social Media Links

1. Go to "Social Media Links"
2. Add Instagram link:
   - Platform: Instagram
   - URL: Your Instagram profile URL
   - Is active: ✓
3. Save

### Customer Flow

1. **Browse Books**: Homepage displays all available books and About section
2. **View Details**: Click on a book to see full details
3. **Add to Cart**: Add books to cart
4. **Checkout**: Fill in customer and delivery details
5. **UPI Payment**: Click "Pay via UPI" button to open UPI apps
6. **Enter Transaction ID**: After payment, enter UPI transaction ID
7. **Confirmation**: Receive order confirmation email

## UPI Payment Flow

The system uses UPI deeplink integration:

- **UPI ID**: nityabhambhani17@oksbi
- **Payee Name**: Nityawrites
- **Amount**: Auto-filled from cart total
- **Note**: "Book Order - Nityawrites"

When customer clicks "Pay via UPI", their installed UPI apps (Google Pay, PhonePe, Paytm, BHIM, etc.) will open with pre-filled payment details.

After payment, customer enters the UPI Transaction ID to confirm the order.

## Email Confirmation

After order confirmation, customers receive an automated email with:
- Order ID
- Books ordered with quantities
- Total amount
- UPI Transaction ID
- Delivery address
- Thank you message

## Project Structure

```
nityawrites.com/
├── nityawrites/          # Project settings
│   ├── settings.py       # Configuration (Email, Static, Media)
│   └── urls.py          # Main URL routing
├── store/               # Main app
│   ├── models.py        # Book, Order, Payment, AboutSection, SocialMedia
│   ├── views.py         # UPI payment & email logic
│   ├── urls.py          # App URLs
│   ├── admin.py         # Admin with Excel export
│   └── templates/       # HTML templates
├── static/              # CSS, JS files
├── media/               # Uploaded images (books, author)
└── requirements.txt     # Dependencies
```

## Models

### Book
- title, author, description, price, stock, image

### Order
- order_id, customer details, address, total_amount, payment_status

### OrderItem
- Links books to orders with quantity and price

### Payment
- upi_transaction_id, order reference, amount, status

### AboutSection
- title, description, author_image, is_active

### SocialMedia
- platform, url, is_active, order

## Excel Export

In the admin panel:
1. Go to Orders
2. Select orders to export
3. Choose "Export to Excel" from Actions dropdown
4. Click "Go"
5. Download the generated Excel file with UPI transaction IDs

## Security Notes

- Change `SECRET_KEY` in production
- Set `DEBUG = False` in production
- Add your domain to `ALLOWED_HOSTS`
- Use environment variables for sensitive data (email password)
- Enable HTTPS in production

## Testing UPI Payment

For testing:
1. Complete checkout with test customer details
2. Click "Pay via UPI" button
3. Complete payment in UPI app
4. Note the UPI Transaction ID
5. Enter transaction ID in the form
6. Verify order confirmation email

## Deployment

For production deployment:
1. Set `DEBUG = False`
2. Configure `ALLOWED_HOSTS`
3. Use PostgreSQL instead of SQLite
4. Set up static file serving
5. Use environment variables for secrets
6. Configure email with production SMTP
7. Enable HTTPS

## Support

For issues or questions, contact: support@nityawrites.com

## License

© 2026 Nityawrites. All rights reserved.
