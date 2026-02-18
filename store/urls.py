from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('book/<int:pk>/', views.book_detail, name='book_detail'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:pk>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:pk>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:pk>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/process/', views.payment_process, name='payment_process'),
    path('payment/upload/<int:order_id>/', views.upload_payment_proof, name='upload_payment_proof'),
    path('payment/callback/', views.payment_callback, name='payment_callback'),
    path('order/success/<str:order_id>/', views.order_success, name='order_success'),
    path('order/failed/', views.order_failed, name='order_failed'),
    path('force-migrate/', views.force_migrate, name='force_migrate'),
    path('create-admin/', views.create_admin, name='create_admin'),

    path('manage-order/verify/<int:pk>/', views.admin_order_verify, name='admin_order_verify'),
    path('manage-order/fail/<int:pk>/', views.admin_order_fail, name='admin_order_fail'),
    path('test-email/', views.test_email_view, name='test_email'),
    path('book/<int:pk>/review/', views.submit_review, name='submit_review'),
]
