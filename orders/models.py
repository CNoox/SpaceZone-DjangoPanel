from django.db import models
from accounts.models import CustomUserModel
from product.models import Product


# Create your models here.
class Order(models.Model):
    user = models.ForeignKey(CustomUserModel,on_delete=models.CASCADE,related_name='order')
    total_price = models.DecimalField(max_digits=14, decimal_places=2,blank=True,null=True)
    total_item = models.PositiveIntegerField(default=0)
    date_order = models.DateTimeField(auto_now_add=True)
    address = models.CharField(max_length=255,blank=True,null=True)
    tracking_code = models.CharField(max_length=200,blank=True,null=True)
    is_success = models.BooleanField(default=False)

    def __str__(self):
        if self.total_price:
            return f"{self.user.email} - {self.total_price:.2f}"
        return self.user.email

    def create(self,request):
        if self.user is None:
            self.user = request.user
            self.save()

    def get_total_price(self):
        return sum(item.get_cost for item in self.items)

class OrderItem(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name='items')
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='order_items')
    order_at = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.product.title + '-' + str(self.quantity)

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
    #     self.order.total_item = sum(i.quantity for i in self.order.item.all())
    #     self.order.total_price = sum(i.product.price * i.quantity for i in self.order.item.all())
    #     self.order.save()

    def get_cost(self):
        return self.product.price * self.quantity