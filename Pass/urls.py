from django.urls import path
from .views import LoginPassView

urlpatterns = [
    # This is the endpoint React will call to exchange a code for a JWT
    path('login-pass/', LoginPassView.as_view(), name='login-pass'),
]