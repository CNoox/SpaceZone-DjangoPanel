from rest_framework import viewsets, status
from .serializers import RegisterSerializer, LoginSerializer, UserPanelSerializer,UserCodeSerializer
from rest_framework.response import Response
from permissions import IsNotAuth
from rest_framework.views import APIView
from .models import CustomUserModel, UserCodeModel
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from datetime import timedelta


class UserSendCodeView(APIView):
    """
    Handles both **login** and **registration** flow using email + password.

    - If user exists → validates credentials and sends a fresh verification code.
    - If user does not exist → automatically registers a new account and issues a verification code.
    - Protects against code spamming by enforcing a cooldown timer.

    Responses:
        - ✅ 201: Returns a new verification code
        - ⚠️ 400: Missing fields or cooldown not expired
        - ❌ 401: Invalid credentials
    """
    permission_classes = [IsNotAuth]
    serializer_class = LoginSerializer

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response({"detail": "Email and Password is required"}, status=400)
        try:
            user = CustomUserModel.objects.get(email=email)
            # Login
            ser_login = LoginSerializer(data=request.data)
            if ser_login.is_valid():
                user = ser_login.validated_data['user']
                try:
                    user_code = UserCodeModel.objects.get(user=user)
                except UserCodeModel.DoesNotExist:
                    user_code = UserCodeModel.objects.create(user=user)
                    code = user_code.create_code()
                    return Response({'code': code}, status=status.HTTP_201_CREATED)
                if user_code.can_request_new():
                    code = user_code.create_code()
                    return Response({'code': code}, status=status.HTTP_201_CREATED)
                else:
                    remaining = user_code.seconds_until_next_code()
                    return Response({"detail": f"Cannot request code yet for {remaining}."}, status=400)
            else:
                return Response(ser_login.errors, status=status.HTTP_401_UNAUTHORIZED)
        except CustomUserModel.DoesNotExist:
            ser_reg = RegisterSerializer(data=request.data)
            if ser_reg.is_valid():
                user = ser_reg.save()
                try:
                    user_code = UserCodeModel.objects.get(user=user)
                except UserCodeModel.DoesNotExist:
                    user_code = UserCodeModel.objects.create(user=user)
                    code = user_code.create_code()
                    return Response({'code': code}, status=status.HTTP_201_CREATED)
                if user_code.can_request_new():
                    code = user_code.create_code()
                    return Response({'code': code}, status=status.HTTP_201_CREATED)
                else:
                    remaining = user_code.seconds_until_next_code()
                    return Response({"detail": f"Cannot request code yet for {remaining}."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(ser_reg.errors, status=status.HTTP_400_BAD_REQUEST)

class UserVerifyCodeView(APIView):
    """
    Verifies a one-time **authentication code** and issues JWT tokens.

    Flow:
        1. User submits a code received via email.
        2. If the code is valid and not expired → returns `access` & `refresh` tokens.
        3. Marks the code as used, preventing re-use.

    Responses:
        - ✅ 200: Returns `access` and `refresh` JWT tokens
        - ❌ 400: Invalid, used, or expired code
    """
    permission_classes = [IsNotAuth]
    serializer_class = UserCodeSerializer
    def post(self, request):
        code = request.data.get("code")
        try:
            user_code = UserCodeModel.objects.get(code=code)
            user = user_code.user
            if user_code.is_used == True:
                return Response({"error": "Invalid or expired code"}, status=status.HTTP_400_BAD_REQUEST)
        except UserCodeModel.DoesNotExist:
            return Response({"error": "Invalid code"}, status=status.HTTP_400_BAD_REQUEST)
        if user_code.expires_code():
            return Response({"error": "Invalid or expired code"}, status=status.HTTP_400_BAD_REQUEST)
        user_code.is_used = True
        user_code.save()
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        return Response({'access':access_token,"refresh": refresh_token},status=status.HTTP_200_OK)

class UserPanelView(APIView):
    """
    Authenticated user’s **personal dashboard**.

    Endpoints:
        - `GET /panel/` → Returns user profile data.
        - `PATCH /panel/` → Updates user profile fields (partial update supported).
        - `DELETE /panel/` → Soft deletes the account (`is_active=False`).

    Permissions:
        - Requires `IsAuthenticated` (JWT token).

    Responses:
        - ✅ 200: Profile retrieved, updated, or deleted
        - ❌ 400: Validation errors on update
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserPanelSerializer
    def get(self,request):
        person = request.user
        ser_person = UserPanelSerializer(instance=person)
        return Response(ser_person.data,status=status.HTTP_200_OK)
    def patch(self,request):
        person = request.user
        person_data = request.data
        ser_person = UserPanelSerializer(instance=person,data=person_data,partial=True)
        if ser_person.is_valid():
            ser_person.save()
            return Response(ser_person.data,status=status.HTTP_200_OK)
        return Response(ser_person.errors,status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request):
        person = request.user
        person.is_active = False
        person.save()
        return Response({'message': 'Account is deleted!'},status=status.HTTP_200_OK)
