from rest_framework import serializers
from .models import Product,Category,ProductComment


class ProductCommentListSerializer(serializers.ModelSerializer):
    latest_comments = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    def get_latest_comments(self, obj):
        comments = obj.comments.order_by('-created_at')[:3]
        return ProductCommentSerializer(comments, many=True).data if comments else []

    def get_category(self, obj):
        category = obj.category
        return UserCategorySetSerializer(category).data if category else None



class ProductCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductComment
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductComment
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        extra_kwargs = {
            'description':{'required':False},
            'slug':{'read_only':True,},
            'image':{'required':False},
            'exist_number':{'required':False},
            'status':{'required':True},
        }

class UserCategorySetSerializer(serializers.ModelSerializer):
    parent = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = ['title','slug','is_active','parent']

    def get_parent(self,obj):
        parent = obj.parent
        if parent:
            return UserCategorySetSerializer(instance=parent).data
        return None

class UserCategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = ['id','title','slug','children']

    def get_children(self,obj):
        children_q = Category.objects.filter(parent=obj)
        return UserCategorySerializer(instance=children_q,many=True,context=self.context).data

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        extra_kwargs = {'slug':{'read_only':True,},
                        'is_active':{'default':True}}

