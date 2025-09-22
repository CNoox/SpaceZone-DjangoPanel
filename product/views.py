
from rest_framework import viewsets,status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Product
from .serializers import ProductCommentListSerializer,ProductCommentSerializer
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

        queryset = queryset.filter(show_item=True)

        queryset = queryset.filter(is_active=True)

        try:
            page_num = int(request.query_params.get('page', 1))
            page_offset = int(request.query_params.get('offset', 10))
            if page_offset < 1:
                page_offset = 1
            elif page_offset > 100:
                page_offset = 100
        except:
            return Response({"detail": "PAGE_NOT_FOUND"}, status=status.HTTP_404_NOT_FOUND)

        paginator = Paginator(queryset, page_offset)
        try:
            page = paginator.page(page_num)
        except:
            return Response({"detail": "PAGE_NOT_FOUND"}, status=status.HTTP_404_NOT_FOUND)
        ser_product = ProductCommentListSerializer(instance=page.object_list, many=True)
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
    http_method_names = ['get']
    queryset = Product.objects.all()
    def retrieve(self,request,slug):
        product = get_object_or_404(self.queryset, slug=slug)
        comments = product.comments.all()

        try:
            page_num = int(request.query_params.get('page', 1))
            page_offset = int(request.query_params.get('offset', 10))
            if page_offset < 1:
                page_offset = 1
            elif page_offset > 100:
                page_offset = 100
        except:
            return Response({"detail": "PAGE_NOT_FOUND"}, status=status.HTTP_404_NOT_FOUND)

        paginator = Paginator(comments, page_offset)
        try:
            page = paginator.page(page_num)
        except:
            return Response({"detail": "PAGE_NOT_FOUND"}, status=status.HTTP_404_NOT_FOUND)

        ser_comment = ProductCommentSerializer(instance=page.object_list, many=True)
        return Response({
            "count_item": paginator.count,
            "count_page": paginator.num_pages,
            "current_page": page_num,
            "results": ser_comment.data
        }, status=status.HTTP_200_OK)





