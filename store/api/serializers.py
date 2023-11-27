from store.models import Product , Cart_Item , Shipping_Addresse

from store.models import ProductCategories , Order_Addr_info , Favored_Item , Purchased_Item

from rest_framework import serializers


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategories
        fields = '__all__'


class Cart_ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart_Item
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class OrderDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order_Addr_info
        fields = '__all__'


class Shipping_AddresseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shipping_Addresse
        exclude = ['user']

    def create(self, validated_data):
        return Shipping_Addresse.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.recepient_fullname = validated_data.get('recepient_fullname', instance.recepient_fullname)
        instance.phone_no = validated_data.get('phone_no', instance.phone_no)
        instance.address_line1 = validated_data.get('address_line1', instance.address_line1)
        instance.address_line2 = validated_data.get('address_line2', instance.address_line2)
        instance.city = validated_data.get('city', instance.city)
        instance.state = validated_data.get('state', instance.state)
        instance.country = validated_data.get('country', instance.country)
        instance.zipcode = validated_data.get('zipcode', instance.zipcode)
        instance.save()
        return instance


class Favored_ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favored_Item
        fields = '__all__'

