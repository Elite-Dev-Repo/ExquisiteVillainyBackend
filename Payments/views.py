import hmac
import hashlib
import requests
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .models import Payment
from Pass.utils import generate_pass_for_payment

class InitializePaymentView(APIView):
    """
    Step 1: Create a local payment record and get the Paystack Auth URL.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        amount = request.data.get('amount')
        
        if not email or not amount:
            return Response({"error": "Email and amount are required"}, status=status.HTTP_400_BAD_REQUEST)

        url = "https://api.paystack.co/transaction/initialize"
        headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
        
        # Paystack expects amount in Kobo (Naira * 100)
        kobo_amount = int(float(amount) * 100)
        
        payload = {
            "email": email,
            "amount": kobo_amount,
            "callback_url": "http://localhost:5173/verify", # Your React Verify Route
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            res_data = response.json()

            if res_data['status']:
                # Create the local record so we can track it
                Payment.objects.create(
                    email=email,
                    amount=kobo_amount,
                    reference=res_data['data']['reference']
                )
                return Response(res_data['data'], status=status.HTTP_200_OK)
            
            return Response(res_data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyPaymentView(APIView):
    """
    Step 2: React calls this after redirect to confirm payment and get the Pass Token.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, reference):
        url = f"https://api.paystack.co/transaction/verify/{reference}"
        headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
        
        response = requests.get(url, headers=headers)
        res_data = response.json()

        if res_data['status'] and res_data['data']['status'] == 'success':
            try:
                payment = Payment.objects.get(reference=reference)
                
                # 1. Update Payment status if not already done
                if not payment.verified:
                    payment.status = 'success'
                    payment.verified = True
                    payment.save()

                # 2. Generate the Pass (utils handles duplicate checks)
                pass_obj = generate_pass_for_payment(payment)
                
                # 3. If pass was already created by Webhook, fetch it
                if not pass_obj:
                    from Pass.models import Pass
                    pass_obj = Pass.objects.filter(payment=payment).first()

                return Response({
                    "status": "success",
                    "pass_code": pass_obj.pass_code if pass_obj else None,
                    "email": payment.email
                }, status=status.HTTP_200_OK)
                
            except Payment.DoesNotExist:
                return Response({"error": "Payment record not found"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({"status": "failed", "message": "Verification failed at Paystack"}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class PaystackWebhookView(APIView):
    """
    Step 3: Background listener for Paystack success signals.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        # Security: Verify the signature
        paystack_signature = request.headers.get('x-paystack-signature')
        secret = settings.PAYSTACK_SECRET_KEY.encode('utf-8')
        computed_hmac = hmac.new(secret, request.body, hashlib.sha512).hexdigest()

        if computed_hmac != paystack_signature:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        payload = request.data
        if payload.get('event') == 'charge.success':
            data = payload.get('data')
            reference = data.get('reference')
            
            try:
                payment = Payment.objects.get(reference=reference)
                
                if not payment.verified:
                    payment.status = 'success'
                    payment.verified = True
                    payment.save()
                    
                    # Automate Pass Generation even if user closed the tab
                    generate_pass_for_payment(payment)
                    
            except Payment.DoesNotExist:
                # Log this internally, but tell Paystack OK to stop retries
                pass

        return Response(status=status.HTTP_200_OK)