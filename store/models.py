from django.db import models
from django.contrib.auth.models import User
import datetime


# Create your models here.

class ProductCategories(models.Model):

    name = models.CharField(max_length=100,blank=False,null=True)
    image = models.ImageField(null=True,blank=False)

    @property
    def get_imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

    def __str__(self):
        return self.name



class Product(models.Model):

    category = models.ManyToManyField(ProductCategories)
    name = models.CharField(max_length=100, blank=False, null=False)
    price = models.FloatField(blank=False,null=False)
    image = models.ImageField(null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    rating = models.DecimalField(max_digits=5, decimal_places=2, blank=True,null=True)
    subcategory = models.CharField(max_length=100, blank=False, null=False)

    @property
    def get_imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

    def __str__(self):
        return '{} - rating:{}'.format(self.name,self.rating)



class Cart_Item(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=False)
    product = models.ForeignKey(Product,on_delete=models.CASCADE,null=True,blank=False)
    date_ordered = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField(default=0,blank=True,null=True)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

    def __str__(self):
        return '{}-{}'.format(self.user.username,self.product.name)



class Shipping_Addresse(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=False)
    name = models.CharField(max_length=100,null=True,blank=False)
    phone_number = models.CharField(max_length=100,null=False,blank=False)
    shipping_address = models.CharField(max_length=200, null=True,blank=False)
    city = models.CharField(max_length=200, null=False)
    state = models.CharField(max_length=200, null=False)
    country = models.CharField(max_length=100,null=True,blank=False)
    zipcode = models.CharField(max_length=200, null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}-{}'.format(self.user.username, self.address_line1)



class Order_Addr_info(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=100,null=True,blank=False)
    phone_number = models.CharField(max_length=100,null=False,blank=False)
    shipping_address = models.CharField(max_length=200, null=True,blank=False)
    city = models.CharField(max_length=200, null=True,blank=False)
    state = models.CharField(max_length=200, null=True,blank=False)
    country = models.CharField(max_length=100, null=True, blank=False)
    zipcode = models.CharField(max_length=200, null=True,blank=False)
    amount = models.IntegerField(null=True,blank=True)
    transaction_id = models.CharField(max_length=100,null=True,blank=False)
    date_ordered = models.DateTimeField(auto_now_add=True,null=True,blank=True)

    def __str__(self):
        return '{}-{}'.format(self.user.username,self.transaction_id)



class Purchased_Item(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    order = models.ForeignKey(Order_Addr_info,on_delete=models.CASCADE,null=True)
    quantity = models.IntegerField(default=0, blank=True, null=True)
    name = models.CharField(max_length=100, blank=False, name=False)
    price = models.FloatField(blank=False, null=True)
    image = models.ImageField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    @property
    def get_imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

    @property
    def get_total(self):
        total = self.price * self.quantity
        return total

    def __str__(self):
        return self.name


class Favored_Item(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    product = models.ForeignKey(Product,on_delete=models.CASCADE,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}-{}'.format(self.user.username,self.product.name)


class Item_Rating(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    product = models.ForeignKey(Product,on_delete=models.CASCADE,null=True,blank=True)
    rating = models.PositiveSmallIntegerField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}--{}: {}'.format(self.user.username,self.product.name,self.rating)

