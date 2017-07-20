from django import forms
from models import UserModel, PostModel,CommentModel,LikeModel
from django.http import HttpResponse


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

class Like_form(forms.ModelForm):
    class Meta:
        model = LikeModel
        fields = ['post']

class Comment_form(forms.ModelForm):
    class Meta:
        model = CommentModel
        fields = ['comment_text', 'post']


