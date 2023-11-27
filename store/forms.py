from django.forms import ModelForm
from .models import Shipping_Addresse

class ShippingForm(ModelForm):
    class Meta:
        model = Shipping_Addresse
        fields = '__all__'
        exclude = ['user']


class ShippingUpdateForm(ModelForm):
    class Meta:
        model = Shipping_Addresse
        fields = '__all__'
        exclude = ['user']
