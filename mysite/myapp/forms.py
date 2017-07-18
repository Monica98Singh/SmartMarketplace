from django import forms
from models import UserModel, PostModel


class Signup_form(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ['name', 'username', 'email', 'password']

class Login_form(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ['username', 'password']

class Post_form(forms.ModelForm):
    class Meta:
        model = PostModel
        fields = ['image', 'caption']
