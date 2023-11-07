from django import forms
from .models import  Profile
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(label = "Password" , widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email'
                  ,'password','confirm_password']

    def clean_confirm_password(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        if password != confirm_password:
            raise forms.ValidationError('Password Mismatch')
        else:
            return confirm_password


class UserUpdateForm(forms.ModelForm):
    # username = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    # email = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email']


class ProfileUpdateForm(forms.ModelForm):
    # Do not use this. For some reason,
    # the 'input type=date' does not work when updating.
    # "Enter a valid date." - keeps this error
    # date_of_birth = forms.DateField(
    #     widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY-MM-DD'}),
    #     input_formats=['YYYY-MM-DD', '%m/%d/%Y', '%d/%m/%Y'],
    # )
    #############################

    class Meta:
        model = Profile
        fields = ['date_of_birth','photo']
