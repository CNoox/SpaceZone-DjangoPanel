from django.contrib import admin
from .models import Product,Category,ProductComment,ProductBuyCheck,AttributeProduct,AttributeValueProduct

# Register your models here.
admin.site.register(Category)
admin.site.register(ProductBuyCheck)
admin.site.register(ProductComment)
admin.site.register(AttributeProduct)
admin.site.register(AttributeValueProduct)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title','price','category','exist_number')
    list_filter = ('category',)