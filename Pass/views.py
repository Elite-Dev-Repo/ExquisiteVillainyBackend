from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Pass

class LoginPassView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        pass_code = request.data.get('pass_code')
        
        if not pass_code:
            return Response({"error": "Pass code is required"}, status=400)

        try:
            user_pass = Pass.objects.get(pass_code__iexact=pass_code)
            
            # Manually generate JWT for this "Guest" identity
            # We add custom claims (email) so the frontend knows who this is
            refresh = RefreshToken()
            refresh['email'] = user_pass.email
            refresh['pass_id'] = user_pass.id

            return Response({
                "status": "success",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "email": user_pass.email
            }, status=status.HTTP_200_OK)

        except Pass.DoesNotExist:
            return Response(
                {"status": "error", "message": "Invalid Pass Token"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )