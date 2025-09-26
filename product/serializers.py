from rest_framework import serializers
from .models import Product,Category,ProductComment,AttributeProduct,AttributeValueProduct


class ProductCommentListSerializer(serializers.ModelSerializer):
    latest_comments = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'
        extra_field = {'latest_comments','category'}

    def get_category(self,obj):
        category = obj.category
        return UserCategorySerializer(instance=category).data

    def get_latest_comments(self, obj):
        comments = obj.comments.order_by('-created_at')[:3]
        if comments:
            return ProductCommentSerializer(instance=comments, many=True).data
        return None



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

class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeProduct
        fields = '__all__'

class AttributeValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeValueProduct
        fields = '__all__'

