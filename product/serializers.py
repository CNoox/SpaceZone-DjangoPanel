from rest_framework import serializers
from .models import Product,Category


class ProductCommentListSerializer(serializers.ModelSerializer):
    latest_comments = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'
        extra_field = {'latest_comments','category'}

    def get_category(self,obj):
        category = obj.category
        if category:
            return CategorySerializer(instance=category).data
        return None

    def get_latest_comments(self, obj):
        comments = obj.comments.order_by('-created_at')[:3]
        return ProductCommentSerializer(instance=comments, many=True).data



class ProductCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        extra_kwargs = {
            'description':{'required':True},
            'slug':{'read_only':True},
            'image':{'required':True},
            'exist_number':{'required':True},
            'status':{'required':True},
        }

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','title','parent']

