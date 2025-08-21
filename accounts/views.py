from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser, VerificationCode
from .serializers import SmartEmailSerializer, VerifyCodeSerializer
from django.utils import timezone

class SmartSendCodeView(APIView):
    """
    Send verification code for either registration or login.
    Includes rate limiting:
    - At least 30 seconds between requests
    - Max 5 codes per day
    """
    def post(self, request):
        serializer = SmartEmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data.get('password')

            user = CustomUser.objects.filter(email=email).first()
            if user:
                if user.is_verified:
                    # Login flow → password must match
                    if not password or not user.check_password(password):
                        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
                    action = "login"
                else:
                    # Registration flow → password required
                    if not password:
                        return Response({"error": "Password is required for registration"}, status=status.HTTP_400_BAD_REQUEST)
                    action = "register"
            else:
                # New registration → password required
                if not password:
                    return Response({"error": "Password is required for registration"}, status=status.HTTP_400_BAD_REQUEST)
                action = "register"
                user = CustomUser.objects.create_user(email=email, password=password)

            # 🔒 Rate limiting
            now = timezone.now()
            last_code = VerificationCode.objects.filter(user=user).order_by("-created_at").first()
            if last_code and (now - last_code.created_at).total_seconds() < 30:
                return Response({"error": "Please wait at least 30 seconds before requesting another code"},
                                status=status.HTTP_400_BAD_REQUEST)

            today_count = VerificationCode.objects.filter(user=user, created_at__date=now.date()).count()
            if today_count >= 5:
                return Response({"error": "You have reached the daily limit of 5 verification codes"},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                # Generate & send verification code
                verification_action = serializer.send_verification_code(email, password)
                return Response({
                    "message": f"Verification code sent for {verification_action}"
                }, status=status.HTTP_200_OK)

            except serializers.ValidationError as e:
                return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailCodeView(APIView):
    """
    Verify the code for registration or login.
    - If registration: just mark user as verified (no token yet).
    - If login: return JWT tokens.
    """
    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']

            user = CustomUser.objects.filter(email=email).first()
            if not user:
                return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)

            verification = VerificationCode.objects.filter(user=user, code=code).order_by("-created_at").first()
            if not verification:
                return Response({"error": "Invalid code"}, status=status.HTTP_400_BAD_REQUEST)

            if verification.is_expired():
                return Response({"error": "Code expired"}, status=status.HTTP_400_BAD_REQUEST)

            if not user.is_verified:
                # Registration complete
                user.is_verified = True
                user.save(update_fields=["is_verified"])
                action = "registration"
                response_data = {
                    "action": action,
                    "message": "Registration verified successfully. Please login."
                }
            else:
                # Login success → issue JWT
                action = "login"
                refresh = RefreshToken.for_user(user)
                response_data = {
                    "action": action,
                    "user": {
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "avatar": user.avatar.url if user.avatar else None,
                        "national_code": user.national_code,
                        "phone_number": user.phone_number
                    },
                    "token": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token)
                    }
                }

            # Consume the verification code
            verification.delete()

            return Response(response_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
