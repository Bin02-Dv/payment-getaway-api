from django.urls import path
from .views import create_payment, handle_payment_callback

urlpatterns = [
    path('api/payments/create/', create_payment, name='create-payment'),
    path('api/payments/callback/', handle_payment_callback, name='handle-payment-callback'),
]
