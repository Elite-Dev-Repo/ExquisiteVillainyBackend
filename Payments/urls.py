from django.urls import path
from .views import InitializePaymentView, VerifyPaymentView, PaystackWebhookView

urlpatterns = [
    path('pay/initialize/', InitializePaymentView.as_view(), name='pay-init'),
    path('pay/verify/<str:reference>/', VerifyPaymentView.as_view(), name='pay-verify'),
    path('pay/webhook/', PaystackWebhookView.as_view(), name='pay-webhook'),
]