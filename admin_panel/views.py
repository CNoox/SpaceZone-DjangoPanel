from rest_framework import status,viewsets
from accounts.serializers import LoginSerializer,UserPanelSerializer,UserVerifyCodeSerializer
from rest_framework.response import Response
from permissions import IsNotAuth,IsSuperUser
from rest_framework.views import APIView
from accounts.models import CustomUserModel, UserCodeModel
from product.models import Product,Category
from product.serializers import ProductCommentListSerializer,ProductSerializer,UserCategorySerializer,CategorySerializer
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from django.core.paginator import Paginator
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.db.models import Min, Max
from django.core.mail import send_mail
from django.conf import settings
from accounts.tasks import send_verification_email

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
                    send_verification_email.delay(
                        subject="Verification-Code",
                        message=f"your auth code: {code}",
                        recipient_list=[email],
                    )
                    return Response({'detail': 'Success!'}, status=status.HTTP_201_CREATED)
                if user_code.can_request_new():
                    if user_code.user.is_superuser == False:
                        return Response({"non_field_errors": [
                            "Invalid email or password"
                        ]}, status=status.HTTP_401_UNAUTHORIZED)
                    code = user_code.create_code()
                    send_verification_email.delay(
                        subject="Verification-Code",
                        message=f"your auth code: {code}",
                        recipient_list=[email],
                    )
                    return Response({'detail': 'Success!'}, status=status.HTTP_201_CREATED)
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
    metadata_class = None

    def list(self,request):
        search = request.query_params.get('search','')
        queryset = self.queryset.filter(Q(email__contains=search) or Q(first_name__icontains=search) or Q(last_name__icontains=search) or Q(phone_number__icontains=search))

        try:
            page_num = int(request.query_params.get('page', 1))
            page_offset = int(request.query_params.get('offset', 10))
        except:
            return Response({"detail": "please right write offset or page"},status=status.HTTP_400_BAD_REQUEST)

        if page_offset < 1:
            page_offset = 1
        elif page_offset > 100:
            page_offset = 100
        paginator = Paginator(queryset, page_offset)
        if page_num < 1:
            page_num = 1
        if page_num > paginator.num_pages:
            page_num = paginator.num_pages
        page = paginator.page(page_num)
        ser_user = UserPanelSerializer(instance=page, many=True)
        return Response({
            "count_item": paginator.count,
            "count_page": paginator.num_pages,
            "current_page": page_num,
            "results": ser_user.data
        }, status=status.HTTP_200_OK)

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
        count = users_delete.count()
        users_delete.update(is_active=False)
        return Response({"detail": f"{count} users deactivated"})

class ProductInformationViewSet(viewsets.ViewSet):
    """
    Manage products by superusers.

    Flow:
        - GET (list): Retrieve a paginated list of products with search, price filter, and sorting
        - POST (create): Create a new product
        - PATCH (partial_update): Update specific fields of a product
        - DELETE (destroy): Soft delete a product
        - POST (`delete` action): Soft delete multiple products

    Query Parameters (GET):
        - search: Filter by title or description
        - sort: newest, oldest, cheapest, expensive
        - min_price: Minimum price
        - max_price: Maximum price
        - page: Page number
        - offset: Items per page

    Responses:
        - ✅ 200: Successfully retrieved or updated products
        - ✅ 201: Product created
        - ❌ 400: Validation error or no IDs provided
        - ❌ 404: Page not found
    """

    permission_classes = [IsSuperUser]
    serializer_class = ProductCommentListSerializer
    queryset = Product.objects.filter()
    metadata_class = None
    def list(self,request):
        queryset = self.queryset

        search = request.query_params.get('search','')
        queryset = queryset.filter(Q(title__icontains=search) or Q(description__icontains=search))

        sort = request.query_params.get('sort', 'newest')
        if sort == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort == 'oldest':
            queryset = queryset.order_by('created_at')
        elif sort == 'cheapest':
            queryset = queryset.order_by('price')
        elif sort == 'expensive':
            queryset = queryset.order_by('-price')
        else:
            queryset = queryset.order_by('-created_at')

        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')

        if min_price is None:
            min_price = Product.objects.aggregate(Min('price'))['price__min'] or 0
        else:
            min_price = float(min_price)

        if max_price is None:
            max_price = Product.objects.aggregate(Max('price'))['price__max'] or 0
        else:
            max_price = float(max_price)

        queryset = queryset.filter(price__gte=min_price, price__lte=max_price)

        queryset = queryset.filter(is_active=True)

        try:
            page_num = int(request.query_params.get('page', 1))
            page_offset = int(request.query_params.get('offset', 10))
        except:
            return Response({"detail": "please right write offset or page"},status=status.HTTP_400_BAD_REQUEST)

        if page_offset < 1:
            page_offset = 1
        elif page_offset > 100:
            page_offset = 100

        paginator = Paginator(queryset, page_offset)

        if page_num < 1:
            page_num = 1
        if page_num > paginator.num_pages:
            page_num = paginator.num_pages
        page = paginator.page(page_num)
        ser_product = ProductCommentListSerializer(instance=page, many=True)
        return Response({
            "count_item": paginator.count,
            "count_page": paginator.num_pages,
            "current_page": page_num,
            "results": ser_product.data
        }, status=status.HTTP_200_OK)

    def partial_update(self,request,pk):
        queryset = self.queryset
        product = get_object_or_404(queryset,slug=pk)
        ser_product = ProductCommentListSerializer(instance=product, data=request.data, partial=True)
        if ser_product.is_valid():
            ser_product.save()
            return Response(ser_product.data,status=status.HTTP_200_OK)
        return Response(ser_product.errors,status=status.HTTP_400_BAD_REQUEST)

    def create(self,request):
        ser_product = ProductSerializer(data=request.data)
        if ser_product.is_valid():
            ser_product.save()
            return Response(ser_product.data,status=status.HTTP_201_CREATED)
        return Response(ser_product.errors,status=status.HTTP_400_BAD_REQUEST)

    def destroy(self,request,pk):
        queryset = self.queryset
        product = get_object_or_404(queryset,slug=pk)
        product.is_active = False
        product.update()
        return Response({"detail":'Product deleted.'},status=status.HTTP_200_OK)

    @action(methods=['post'],detail=False)
    def delete(self,request):
        ids = request.data.get('ids',[])
        if not ids:
            return Response({"detail": "No IDs provided"}, status=status.HTTP_400_BAD_REQUEST)
        product_delete = Product.objects.filter(id__in=ids,is_active=True)
        if not product_delete.exists():
            return Response({"detail": "No IDs provided"}, status=status.HTTP_400_BAD_REQUEST)
        count = product_delete.count()
        product_delete.update(is_active=False)
        return Response({"detail": f"{count} product deleted"})

class AdminCategoryViewSet(viewsets.ViewSet):
    """
    Manage categories by superusers.

    Flow:
        - GET (list): Retrieve all active categories
        - POST (create): Create a new category
        - PATCH (partial_update): Update specific fields of a category
        - DELETE (destroy): Soft delete a category
        - POST (`delete` action): Soft delete multiple categories

    Responses:
        - ✅ 200: Successfully retrieved or updated categories
        - ✅ 201: Category created
        - ❌ 400: Validation error or no IDs provided
    """
    permission_classes = [IsSuperUser]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    metadata_class = None

    def list(self,request):
        queryset = self.queryset
        category = queryset.filter(is_active=True)
        category = category.filter(parent__isnull=True)
        ser_cat = UserCategorySerializer(instance=category, many=True)
        return Response(ser_cat.data,status=status.HTTP_200_OK)

    def create(self,request):
        ser_cat = CategorySerializer(data=request.data)
        if ser_cat.is_valid():
            ser_cat.save()
            return Response(ser_cat.data,status=status.HTTP_201_CREATED)
        return Response(ser_cat.errors,status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self,request,pk):
        queryset = self.queryset
        category = get_object_or_404(queryset,slug=pk)
        ser_cat = CategorySerializer(instance=category, data=request.data, partial=True)
        if ser_cat.is_valid():
            ser_cat.save()
            return Response(ser_cat.data, status=status.HTTP_201_CREATED)
        return Response(ser_cat.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self,request,pk):
        queryset = self.queryset
        queryset = get_object_or_404(queryset,slug=pk)
        if queryset.is_active == False:
            return Response("BAD_REQUEST",status.HTTP_400_BAD_REQUEST)
        queryset.is_active = False
        queryset.save()
        return Response({"detail":'Category deleted.'},status=status.HTTP_200_OK)

    @action(methods=['post'],detail=False)
    def delete(self,request):
        ids = request.data.get('ids',[])
        if not ids:
            return Response({"detail": "No IDs provided"}, status=status.HTTP_400_BAD_REQUEST)
        category_delete = Category.objects.filter(id__in=ids,is_active=True)
        if not category_delete.exists():
            return Response({"detail": "No IDs provided"}, status=status.HTTP_400_BAD_REQUEST)
        count = category_delete.count()
        category_delete.update(is_active=False)
        return Response({"detail": f"{count} category deleted"})


class AdminSelectCategoryViewSet(viewsets.ViewSet):
    """
    Provides a list of active categories without children for frontend select boxes.

    Features:
        - GET (list): Retrieve all active categories that have no children.
        - Optional search: filter categories by title using `?search=<query>`.

    Flow:
        1. Frontend requests categories for a select box.
        2. Only active categories without children are returned.
        3. Optional `search` query parameter can filter by category title.

    Responses:
        - ✅ 200: Successfully retrieved categories.
        - ❌ 400: Invalid query parameters (if implemented in the future).
    """
    permission_classes = [IsSuperUser]
    queryset = Category.objects.all()
    serializer_class = UserCategorySerializer
    metadata_class = None
    http_method_names = ['get']
    def list(self,request):
        queryset = self.queryset
        category = queryset.filter(is_active=True)
        category = category.filter(parent__isnull = True)
        search = request.query_params.get('search','')
        if search:
            category = category.filter(title__icontains=search)
        ser_cat = UserCategorySerializer(instance=category, many=True)
        return Response(ser_cat.data,status=status.HTTP_200_OK)

