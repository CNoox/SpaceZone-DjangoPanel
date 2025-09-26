from django.db import models
from accounts.models import CustomUserModel
from django.utils.text import slugify

# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=100,unique=True)
    slug = models.SlugField(max_length=100,unique = True,allow_unicode=True)
    parent = models.ForeignKey('self',on_delete=models.CASCADE,related_name='children',blank=True,null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        if self.parent:
            return f'{self.title} - {self.parent.title}'
        return self.title

    def save(self, *args, **kwargs):

        if not self.slug or self.slug != slugify(self.title,allow_unicode=True):
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

def get_product_image(self,filename):
    return 'product/product_image'+ str(self.pk) +'/product_image.png'
def get_default_image():
    return 'product/default_image/default_product_image.png'

class Product(models.Model):
    title = models.CharField(max_length=150,unique=True)
    slug = models.SlugField(unique=True, blank=True,allow_unicode=True)
    description = models.TextField(blank=False,null=False)
    price = models.DecimalField(max_digits=14, decimal_places=2,blank=False,null=False)
    category = models.ForeignKey(Category,on_delete=models.CASCADE,related_name='product')
    image = models.ImageField(upload_to=get_product_image,default=get_default_image)
    exist_number = models.PositiveIntegerField(blank=False,null=False)
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('unavailable', 'Unavailable'),
        ('pending', 'Pending'),
    )
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    show_item = models.BooleanField(blank=False,null=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.title} - {self.category.title}'


    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)

        if self.exist_number == 0:
            if self.status != 'pending':
                self.status = 'unavailable'
        else:
            self.status = 'available'
        super().save(*args, **kwargs)

class ProductComment(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='comments')
    author = models.ForeignKey(CustomUserModel,on_delete=models.CASCADE,related_name='comments')
    text_comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.author.email} - {self.text_comment[:30]}"


class ProductBuyCheck(models.Model):
    product = models.ForeignKey(Product,on_delete=models.PROTECT,related_name='buy_check')
    user = models.ForeignKey(CustomUserModel,on_delete=models.CASCADE,related_name='buy_check')
    is_success = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.user.email} - {self.product.title}'


class AttributeProduct(models.Model):
    title = models.CharField(max_length=100)
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='attrs')

    def __str__(self):
        return f'{self.title} - {self.product}'

class AttributeValueProduct(models.Model):
    value = models.CharField(max_length=50)
    attr = models.ForeignKey(AttributeProduct,on_delete=models.CASCADE,related_name='value')