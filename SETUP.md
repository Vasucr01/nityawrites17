# Quick Setup Guide - Nityawrites.com

## Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 2: Configure Email
Edit `nityawrites/settings.py`:
```python
EMAIL_HOST_USER = 'your_email@gmail.com'
EMAIL_HOST_PASSWORD = 'your_gmail_app_password'
DEFAULT_FROM_EMAIL = 'Nityawrites <your_email@gmail.com>'
```

**Get Gmail App Password:**
- Google Account → Security → 2-Step Verification → App passwords
- Generate password for "Mail"

## Step 3: Setup Database
```bash
python manage.py migrate
```

## Step 4: Create Admin User
```bash
python manage.py createsuperuser
```

## Step 5: Run Server
```bash
python manage.py runserver
```

## Access Points
- **Website**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## First Steps in Admin
1. Login to admin panel
2. Add books with images, prices, descriptions
3. Create "About Section" with author info and image
4. Add Instagram link in "Social Media Links"
5. Test the shopping flow on main site

## UPI Payment
- **UPI ID**: nityabhambhani17@oksbi
- Payment opens UPI apps directly
- Customer enters transaction ID after payment

## Important Notes
- Configure email before testing (orders send confirmation emails)
- Add About section to display on homepage
- Add Instagram link for social media integration
- Stock automatically decreases after successful orders
- Export orders to Excel from admin panel
