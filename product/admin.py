from django.contrib import admin
from .models import Product,Category,Order,OrderItem,Attribute,ProductAttributeValue,ProductComment

# Register your models here.
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Attribute)
admin.site.register(ProductAttributeValue)

admin.site.register(ProductComment)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title','price','category','exist_number')
    list_filter = ('category',)