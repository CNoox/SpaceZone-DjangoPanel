from rest_framework import status,viewsets
from accounts.serializers import LoginSerializer,UserPanelSerializer,UserVerifyCodeSerializer
from rest_framework.response import Response
from permissions import IsNotAuth,IsSuperUser
from rest_framework.views import APIView
from accounts.models import CustomUserModel, UserCodeModel
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from pagination import CustomPageNumberPagination
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

# Create your views here.

class AdminSendCodeView(APIView):
    """
    Sends a one-time **authentication code** to superusers for login.

    Flow:
        1. User submits email and password.
        2. If credentials are valid and user is superuser → creates or reuses a code.
        3. Returns the code or remaining wait time if code cannot be requested yet.

    Responses:
        - ✅ 201: Returns the authentication code.
        - ❌ 400: Email or password missing, or cannot request code yet.
        - ❌ 401: Invalid email, password, or user is not a superuser.
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
                    if user_code.user.is_superuser == False:
                        return Response({"non_field_errors": [
                            "Invalid email or password"
                        ]}, status=status.HTTP_401_UNAUTHORIZED)
                    code = user_code.create_code()
                    return Response({'code': code}, status=status.HTTP_201_CREATED)
                if user_code.can_request_new():
                    if user_code.user.is_superuser == False:
                        return Response({"non_field_errors": [
                            "Invalid email or password"
                        ]}, status=status.HTTP_401_UNAUTHORIZED)
                    code = user_code.create_code()
                    return Response({'code': code}, status=status.HTTP_201_CREATED)
                else:
                    if user_code.user.is_superuser == False:
                        return Response({"non_field_errors": [
                            "Invalid email or password"
                        ]}, status=status.HTTP_401_UNAUTHORIZED)
                    remaining = user_code.seconds_until_next_code()
                    return Response({"detail": f"Cannot request code yet for {remaining}."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(ser_login.errors, status=status.HTTP_401_UNAUTHORIZED)
        except CustomUserModel.DoesNotExist:
            return Response({"non_field_errors": [
                "Invalid email or password"
            ]}, status=status.HTTP_401_UNAUTHORIZED)

class AdminVerifyCodeView(APIView):
    """
    Verifies a one-time **authentication code** and issues JWT tokens.

    Flow:
        1. User submits the code received via email.
        2. If the code is valid and belongs to a superuser → returns `access` & `refresh` tokens.

    Responses:
        - ✅ 200: Returns `access` and `refresh` JWT tokens.
        - ❌ 400: Invalid, used, or expired code, or user is not a superuser.
    """
    permission_classes = [IsNotAuth]
    serializer_class = UserVerifyCodeSerializer

    def post(self, request):
        ser_data = UserVerifyCodeSerializer(data=request.data)
        if ser_data.is_valid():
            user = CustomUserModel.objects.get(email=ser_data.validated_data['email'])
            if user.is_superuser == False:
                return Response({"detail": "HTTP_400_BAD_REQUEST"}, status=status.HTTP_400_BAD_REQUEST)
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            access_token.set_exp(lifetime=timedelta(minutes=15))
            return Response({"access": str(access_token), "refresh": str(refresh)}, status=status.HTTP_200_OK)
        return Response(ser_data.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminPanelView(APIView):
    """
    Provides a **personal dashboard** for authenticated superusers.

    Flow:
        - GET: Returns the profile data of the requesting superuser.
        - PATCH: Updates the superuser's profile partially.

    Responses:
        - ✅ 200: Profile retrieved, updated, or deleted successfully.
        - ❌ 400: Validation errors on update.
        - ❌ 401/403: Unauthorized or permission denied.
    """
    permission_classes = [IsSuperUser]
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
        return Response({"detail": "Method \"DELETE\" not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
class UserInformationViewSet(viewsets.ModelViewSet):
    """
    Manages **normal users** (non-superusers) by superusers.

    Flow:
        - GET (list/retrieve): Returns users' profile data with pagination.
        - PATCH (partial_update): Updates specified fields of a user.
        - POST (`user_delete` action): Soft deletes multiple users.

    Responses:
        - ✅ 200: Users retrieved, updated, or deactivated successfully.
        - ❌ 400: Validation errors or no IDs provided for deletion.
        - ❌ 401/403: Unauthorized or permission denied.
        - ❌ 405: POST, PUT, or DELETE methods not allowed (default endpoints).
    """
    permission_classes = [IsSuperUser]
    serializer_class = UserPanelSerializer
    queryset = CustomUserModel.objects.filter(is_superuser=False)
    pagination_class = CustomPageNumberPagination
    metadata_class = None

    def create(self, request, *args, **kwargs):
        return Response({"detail": "Method \"POST\" not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response({"detail": "Method \"PUT\" not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self,request,pk):
        user = get_object_or_404(self.queryset,pk=pk)
        ser_user = UserPanelSerializer(instance=user,data=request.data,partial=True)
        if ser_user.is_valid():
            ser_user.save()
            return Response(ser_user.data,status=status.HTTP_200_OK)
        return Response(ser_user.errors,status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "Method \"DELETE\" not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=False,methods=['post'])
    def user_delete(self,request):
        ids = request.data.get('ids',[])
        if not ids:
            return Response({"detail": "No IDs provided"}, status=status.HTTP_400_BAD_REQUEST)
        users_delete = CustomUserModel.objects.filter(id__in=ids,is_superuser=False)
        if not users_delete.exists():
            return Response({"detail": "No IDs provided"}, status=status.HTTP_400_BAD_REQUEST)
        users_delete.update(is_active=False)
        return Response({"detail": f"{users_delete.count()} users deactivated"})
