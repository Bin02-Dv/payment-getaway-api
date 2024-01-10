from django.shortcuts import render

# Create your views here.

# views.py

import paypalrestsdk
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Payment
from django.http import HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

paypalrestsdk.configure({
    'mode': settings.PAYPAL_MODE,
    'client_id': settings.PAYPAL_CLIENT_ID,
    'client_secret': settings.PAYPAL_SECRET,
})

def create_payment(request):
    # Assuming you have a form or some mechanism to get the payment amount from the request
    amount = request.POST.get('amount', '0.00')

    payment = paypalrestsdk.Payment({
        'intent': 'sale',
        'payer': {'payment_method': 'paypal'},
        'transactions': [{
            'amount': {'total': amount, 'currency': 'NGN'},  # Use 'NGN' for Nigerian Naira
            'description': 'Payment description',
        }],
        'redirect_urls': {
            'return_url': 'http://example.com/success',
            'cancel_url': 'http://example.com/cancel',
        },
    })

    if payment.create():
        # Save payment details to your database
        Payment.objects.create(
            amount=amount,
            currency='NGN',
            status='pending',
            transaction_id=payment.id,
        )

        return JsonResponse({'payment_url': payment.links[1].href})
    else:
        return JsonResponse({'error': payment.error})

def verify_payment_with_paymentx(data, requests):
    # Extract necessary information from the callback data
    payment_id = data.get('payment_id')  # Replace 'payment_id' with the actual field in the callback
    payment_amount = data.get('amount')  # Replace 'amount' with the actual field in the callback
    # ... other relevant data

    # Call PaymentX API to verify the payment
    # Replace the following lines with the actual code to verify the payment with PaymentX API
    # Example: Make an API request to PaymentX to check the payment status
    paymentx_api_url = 'https://api.paymentx.com/verify_payment'
    response = requests.post(paymentx_api_url, data={'payment_id': payment_id, 'amount': payment_amount})
    
    # Check if the API response indicates a successful payment verification
    if response.status_code == 200 and response.json().get('status') == 'success':
        return True
    else:
        return False

@require_POST
@csrf_exempt
def handle_payment_callback(request):
    # Extract data from the request
    data = request.data
    payment_id = data.get('payment_id')  # Replace 'payment_id' with the actual field in the callback

    # Retrieve the corresponding payment from your database
    try:
        payment = Payment.objects.get(id=payment_id)
    except Payment.DoesNotExist:
        return HttpResponseBadRequest("Invalid payment ID")

    # Verify the payment status using your payment provider's API or IPN verification
    is_payment_verified = verify_payment_with_paymentx(data)  # Implement this function based on your payment provider

    if is_payment_verified:
        # Update the payment status in your database
        payment.status = 'completed'
        payment.save()

        # Additional logic based on your application requirements

        return Response({'status': 'success'}, status=status.HTTP_200_OK)
    else:
        # Payment verification failed, update the status accordingly
        payment.status = 'failed'
        payment.save()

        # Log the verification failure or handle it as needed

        return HttpResponseBadRequest("Payment verification failed")
