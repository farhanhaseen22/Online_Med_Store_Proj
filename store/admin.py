from django.contrib import admin
from . import models

admin.site.register(models.Product)
admin.site.register(models.ProductCategories)
admin.site.register(models.Cart_Item)
admin.site.register(models.Shipping_Addresse)
admin.site.register(models.Order_Addr_info)
admin.site.register(models.Purchased_Item)
admin.site.register(models.Favored_Item)
admin.site.register(models.Item_Rating)
