from django.db import models
from accounts.models import CustomUserModel
from django.utils.text import slugify

# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=100,unique=True)
    slug = models.SlugField(max_length=100,unique = True,allow_unicode=True,blank=True,null=True)
    parent = models.ForeignKey('self',on_delete=models.CASCADE,related_name='children',blank=True,null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        if self.parent:
            return f'{self.title} - {self.parent.title}'
        return self.title

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)


def get_product_image(self,filename):
    return 'product/product_image'+ str(self.pk) +'/product_image.png'
def get_default_image():
    return 'product/default_image/default_product_image.png'

class Product(models.Model):
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('unavailable', 'Unavailable'),
        ('pending', 'Pending'),
    )
    title = models.CharField(max_length=150,unique=True)
    slug = models.SlugField(unique=True, blank=True,allow_unicode=True)
    description = models.TextField(blank=True,null=True)
    price = models.DecimalField(max_digits=14, decimal_places=2,blank=False,null=False)
    category = models.ForeignKey(Category,on_delete=models.CASCADE,related_name='product')
    image = models.ImageField(upload_to=get_product_image,default=get_default_image)
    exist_number = models.IntegerField(blank=False,null=False)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    show_item = models.BooleanField(blank=False,null=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        if self.category:
            return f'{self.title} - {self.category.title}'
        return self.title


    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)

        if self.exist_number is None or self.exist_number == 0:
            if self.status != 'pending':
                self.status = 'unavailable'
        else:
            self.status = 'available'
        super().save(*args, **kwargs)

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
    address = models.CharField(max_length=255)
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


class ProductComment(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='comments')
    author = models.ForeignKey(CustomUserModel,on_delete=models.CASCADE,related_name='comments')
    text_comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.author.email} - {self.text_comment[:30]}"