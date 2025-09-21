from django.db import models
from accounts.models import CustomUserModel

# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=100,unique=True)
    slug = models.SlugField(max_length=100,unique = True,allow_unicode=True)
    parent = models.ForeignKey('self',on_delete=models.CASCADE,related_name='children',blank=True,null=True)

    def __str__(self):
        if self.parent:
            return f'{self.title} - {self.parent.title}'
        return self.title

def get_product_image(self,filename):
    return 'product/product_image'+ str(self.pk) +'/product_image.png'
def get_default_image():
    return 'product/default_image/default_product_image.png'

class Product(models.Model):
    title = models.CharField(max_length=150,unique=True)
    slug = models.SlugField(max_length=200,unique = True,allow_unicode=True)
    description = models.TextField(blank=True,null=True)
    price = models.DecimalField(max_digits=14, decimal_places=2,blank=True,null=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE,related_name='product')
    image = models.ImageField(upload_to=get_product_image,default=get_default_image)
    exist_number = models.IntegerField(default=0,blank=True,null=True)

    def __str__(self):
        if self.category:
            return f'{self.title} - {self.category.title}'
        return self.title

class Attribute(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="attributes")
    title = models.CharField(max_length=60)

    def __str__(self):
        return f'{self.category.title} - {self.title}'

class Order(models.Model):
    user = models.ForeignKey(CustomUserModel,on_delete=models.CASCADE,related_name='order')
    total_price = models.DecimalField(max_digits=14, decimal_places=2,blank=True,null=True)
    total_item = models.IntegerField(default=0,blank=True,null=True)
    date_order = models.DateTimeField(auto_now_add=True)
    tracking_code = models.CharField(max_length=200,blank=True,null=True)

    def __str__(self):
        if self.total_price:
            return f"{self.user.email} - {self.total_price:.2f}"
        return self.user.email

class OrderItem(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name='item')
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='order_items')
    order_at = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField(default=0,blank=True,null=True)

    def __str__(self):
        return self.product.title + '-' + str(self.quantity)

class ProductAttributeValue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="attribute_values")
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.product.title} - {self.attribute.title}: {self.value}"