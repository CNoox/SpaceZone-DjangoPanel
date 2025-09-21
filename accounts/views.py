from rest_framework import viewsets, status
from .serializers import RegisterSerializer, LoginSerializer, UserPanelSerializer, UserVerifyCodeSerializer ,SendCodeForgetUserSerializer ,UpdatePasswordSerializer
from rest_framework.response import Response
from permissions import IsNotAuth,IsNotSuperUser
from rest_framework.views import APIView
from .models import CustomUserModel, UserCodeModel
from rest_framework_simplejwt.tokens import RefreshToken
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
            return Response({"detail": "Email and Password is required"}, status=status.HTTP_400_BAD_REQUEST)
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
                    if user_code.user.is_superuser == True:
                        return Response({    "non_field_errors": [
        "Invalid email or password"
    ]},status=status.HTTP_401_UNAUTHORIZED)
                    code = user_code.create_code()
                    return Response({'code': code}, status=status.HTTP_201_CREATED)
                if user_code.can_request_new():
                    if user_code.user.is_superuser == True:
                        return Response({    "non_field_errors": [
        "Invalid email or password"
    ]},status=status.HTTP_401_UNAUTHORIZED)
                    code = user_code.create_code()
                    return Response({'code': code}, status=status.HTTP_201_CREATED)
                else:
                    if user_code.user.is_superuser == True:
                        return Response({"non_field_errors": [
                            "Invalid email or password"
                        ]}, status=status.HTTP_401_UNAUTHORIZED)
                    remaining = user_code.seconds_until_next_code()
                    return Response({"detail": f"Cannot request code yet for {remaining}."}, status=status.HTTP_400_BAD_REQUEST)
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

    Responses:
        - ✅ 200: Returns `access` and `refresh` JWT tokens
        - ❌ 400: Invalid, used, or expired code
    """
    permission_classes = [IsNotAuth]
    serializer_class = UserVerifyCodeSerializer
    def post(self, request):
        ser_data = UserVerifyCodeSerializer(data=request.data)
        if ser_data.is_valid():
            user = CustomUserModel.objects.get(email=ser_data.validated_data['email'])
            if user.is_superuser == True:
                return Response({"detail":"HTTP_400_BAD_REQUEST"},status=status.HTTP_400_BAD_REQUEST)
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            access_token.set_exp(lifetime=timedelta(minutes=15))
            return Response({"access": str(access_token),"refresh": str(refresh)},status=status.HTTP_200_OK)
        return Response(ser_data.errors,status=status.HTTP_400_BAD_REQUEST)

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
    permission_classes = [IsNotSuperUser]
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

class SendCodeForgetUserView(APIView):
    """
    Sends a one-time **authentication code** to the user for password reset.

    Flow:
        1. User submits their email.
        2. If the email exists and a new code can be requested → generates & returns a code.
        3. Code expires after a short time (e.g., 5 minutes).

    Permissions:
        - Requires `IsNotAuth` (user must NOT be authenticated).

    Responses:
        - ✅ 201: Code successfully generated and returned
        - ❌ 400: Invalid email or request too soon
    """
    permission_classes = [IsNotAuth]
    serializer_class = SendCodeForgetUserSerializer
    def post(self,request):
        ser_person = SendCodeForgetUserSerializer(data=request.data)
        if ser_person.is_valid():
            return Response({'code': ser_person.save()},status=status.HTTP_201_CREATED)
        return Response(ser_person.errors,status=status.HTTP_400_BAD_REQUEST)

class UpdatePasswordView(APIView):
    """
    Changes the authenticated user’s password.

    Flow:
        1. User provides new password (and confirmation).
        2. Password policy is checked.
        3. Password is updated and hashed.
        4. All JWT tokens can be invalidated after the change.

    Permissions:
        - Requires `IsAuthenticated` (JWT token).

    Responses:
        - ✅ 200: Password successfully changed
        - ❌ 400: Validation errors (e.g., weak password, mismatch)
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UpdatePasswordSerializer

    def patch(self,request):
        ser_user = UpdatePasswordSerializer(instance=request.user,data=request.data)
        if ser_user.is_valid():
            ser_user.save()
            return Response('Password changed.',status=status.HTTP_200_OK)
        return Response(ser_user.errors,status=status.HTTP_400_BAD_REQUEST)