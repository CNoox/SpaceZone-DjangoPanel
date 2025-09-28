
from rest_framework import viewsets,status,views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from permissions import IsOwnerOrReadOnly
from .models import Product,ProductComment,Category
from .serializers import ProductCommentListSerializer,CommentSerializer,UserCategorySerializer
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models import Min, Max
from django.shortcuts import get_object_or_404

# Create your views here.

class ProductViewSet(viewsets.ModelViewSet):
    """
    Retrieve products with search, filtering, and pagination.

    Flow:
        - GET (list): Get a list of products with optional search, price filter, and sorting

    Query Parameters (GET):
        - search: Filter by title or description
        - sort: newest, oldest, cheapest, expensive
        - min_price: Minimum price
        - max_price: Maximum price
        - page: Page number
        - offset: Number of items per page

    Filters Applied:
        - show_item: True
        - is_active: True

    Responses:
        - ✅ 200: Successfully retrieved products with pagination info and min/max price
        - ❌ 404: Page not found
    """
    permission_classes = [AllowAny]
    queryset = Product.objects.all()
    serializer_class = ProductCommentListSerializer
    http_method_names = ['get']
    lookup_field = 'slug'
    metadata_class = None

    def list(self,request):
        queryset = self.queryset

        search = request.query_params.get('search','')
        if search:
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
        if min_price is None:
            min_price = Product.objects.aggregate(Min('price'))['price__min'] or 0
        else:
            min_price = float(min_price)

        max_price = request.query_params.get('max_price')
        if max_price is None:
            max_price = Product.objects.aggregate(Max('price'))['price__max'] or 0
        else:
            max_price = float(max_price)

        queryset = queryset.filter(price__gte=min_price, price__lte=max_price)

        queryset = queryset.filter(Q(show_item=True) and Q(is_active=True))

        try:
            page_num = int(request.query_params.get('page', 1))
            page_offset = int(request.query_params.get('offset', 10))
        except:
            return Response({"detail": "please right write offset or page"},status=status.HTTP_400_BAD_REQUEST)

        sort = request.query_params.get('sort','')
        if sort == '-created_at' or sort:
            queryset = queryset.order_by('-created_at')
        if sort == 'created_at':
            queryset = queryset.order_by('created_at')
        else:
            queryset = queryset.order_by('-created_at')


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
            "results": ser_product.data,
            "max_price": max_price,
            "min_price": min_price,
        }, status=status.HTTP_200_OK)

class CommentViewsSet(viewsets.ViewSet):
    """
    Retrieve comments for a specific product with pagination.

    Flow:
        - GET (retrieve): Get a paginated list of comments for a product identified by its slug

    Query Parameters (GET):
        - page: Page number
        - offset: Number of items per page

    Responses:
        - ✅ 200: Successfully retrieved comments with pagination info
        - ❌ 404: Page not found
    """
    permission_classes = [IsOwnerOrReadOnly]
    http_method_names = ['get','patch']
    queryset = Product.objects.all()
    serializer_class = CommentSerializer
    def retrieve(self,request,slug):
        product = get_object_or_404(self.queryset, slug=slug)
        comments = product.comments.all()

        try:
            page_num = int(request.query_params.get('page', 1))
            page_offset = int(request.query_params.get('offset', 10))
        except:
            return Response({"detail": "please right write offset or page"},status=status.HTTP_400_BAD_REQUEST)

        sort = request.query_params.get('sort','')
        if sort == '-created_at' or sort:
            comments = comments.order_by('-created_at')
        if sort == 'created_at':
            comments = comments.order_by('created_at')
        else:
            comments = comments.order_by('-created_at')


        if page_offset < 1:
            page_offset = 1
        elif page_offset > 100:
            page_offset = 100

        paginator = Paginator(product, page_offset)

        if page_num < 1:
            page_num = 1
        if page_num > paginator.num_pages:
            page_num = paginator.num_pages
        page = paginator.page(page_num)

        ser_comment = CommentSerializer(instance=page.object_list, many=True)
        return Response({
            "count_item": paginator.count,
            "count_page": paginator.num_pages,
            "current_page": page_num,
            "results": ser_comment.data
        }, status=status.HTTP_200_OK)

    def partial_update(self,request,slug,pk):
        product = get_object_or_404(self.queryset,slug=slug)
        comments = get_object_or_404(product.comments,pk=pk)
        if request.user != comments.author and not request.user.is_superuser:
            return Response('You dont have access to this content!')
        ser = CommentSerializer(instance=comments,data=request.data,partial=True)
        if ser.is_valid():
            ser.save()
            return Response(ser.data,status=status.HTTP_200_OK)
        return Response(ser.errors,status=status.HTTP_400_BAD_REQUEST)


class CategoryView(views.APIView):
    permission_classes = [AllowAny]
    serializer_class = UserCategorySerializer
    def get(self,request):
        category = Category.objects.filter(parent__isnull=True)
        ser_cat = UserCategorySerializer(instance=category,many=True)
        return Response(ser_cat.data,status=status.HTTP_200_OK)

class CategoryProductView(views.APIView):
    permission_classes = [AllowAny]
    serializer_class = ProductCommentListSerializer

    def get(self, request, slug):
        category = get_object_or_404(Category, slug=slug)

        def get_cat_ids(cat):
            ids = []
            queue = [cat]
            while queue:
                current = queue.pop(0)
                ids.append(current.id)
                queue.extend(current.children.all())
            return ids

        cat_id = get_cat_ids(category)
        product = Product.objects.filter(category_id__in=cat_id)

        try:
            page_num = int(request.query_params.get('page', 1))
            page_offset = int(request.query_params.get('offset', 10))
        except:
            return Response({"detail": "please right write offset or page"}, status=status.HTTP_400_BAD_REQUEST)

        sort = request.query_params.get('sort', '')
        if sort == '-created_at' or sort:
            product = product.order_by('-created_at')
        elif sort == 'created_at':
            product = product.order_by('created_at')
        else:
            product = product.order_by('-created_at')

        if page_offset < 1:
            page_offset = 1
        elif page_offset > 100:
            page_offset = 100

        paginator = Paginator(product, page_offset)

        if page_num < 1:
            page_num = 1
        elif page_num > paginator.num_pages:
            page_num = paginator.num_pages
        page = paginator.page(page_num)

        ser_pro = ProductCommentListSerializer(instance=page.object_list, many=True)
        return Response({
            "count_item": paginator.count,
            "count_page": paginator.num_pages,
            "current_page": page_num,
            "results": ser_pro.data
        }, status=status.HTTP_200_OK)



# class CategoryProductClass(views.APIView):
#

