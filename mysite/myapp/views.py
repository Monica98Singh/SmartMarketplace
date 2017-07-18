# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta
from django.shortcuts import render, redirect
from django.utils import timezone

from forms import Signup_form, Login_form, Post_form
from models import UserModel, SessionToken, PostModel
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password
#from imgurpython import ImgurClient
from mysite.settings import BASE_DIR
import re
import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()
import os


import cloudinary
import cloudinary.api
import cloudinary.uploader


# Create your views here.
from django.utils.datetime_safe import datetime

'''for imgur
CLIENT_ID = 'ff5b64065fa26a5'
CLIENT_SECRET = '4d3de558e74f2537d5b74bba32ebe470bfbad933'''

API_Key = '564665283213574'
API_Secret = 'I35M1dR4ztrh8bJoG3OZ0nGEfQ4'
cloud_name = 'acadview'




def signup_view(request):
    if request.method == 'GET':
        form = Signup_form()
    elif request.method == 'POST':
        form = Signup_form(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            '''if len(username)>2:
                raise form.ValidationError('Not entered anything')
            else:
                pass'''
            # saving data to database
            user = UserModel(name=name, username=username, email=email, password=make_password(password))
            user.save()
            return render(request, 'success.html')
            # return redirect('login/')
    return render(request, 'index.html', {'signup_form': form})


def login_view(request):
    response_data = {}
    if request.method == "POST":
        form = Login_form(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = UserModel.objects.filter(username=username).first()

            if user:
                if check_password(password, user.password):
                    token = SessionToken(user=user)
                    token.create_token()
                    token.save()
                    response = redirect('feed/')
                    response.set_cookie(key='session_token', value=token.session_token)
                    return response
                else:
                    response_data['message'] = 'Incorrect Password! Please try again!'

    elif request.method == 'GET':
        form = Login_form()


    response_data['form'] = form
    return render(request, 'login.html', response_data)




def post_view(request):
    user = check_validation(request)


    if user:
        if request.method == 'POST':
            form = Post_form(request.POST, request.FILES)
            if form.is_valid():
                image = form.cleaned_data.get('image')
                caption = form.cleaned_data.get('caption')
                post = PostModel(user=user, image=image, caption=caption)
                #import pdb; pdb.set_trace()
                files = post.image.url
                post.save()

                pat=os.path.join(BASE_DIR,files)
                # pat = str(BASE_DIR +'//'+ files)
                #ht = re.sub(r'/', r'\\', pat)

                '''client = ImgurClient(CLIENT_ID, CLIENT_SECRET)
                post.image_url = client.upload_from_path(path,anon=True)['link']'''

                '''def upload(file, cloud_name, API_Key, API_Secret):
                    cloudinary.config(cloud_name=cloud_name, API_Key=API_Key, API_Secret=API_Secret)
                    cloudinary.uploader.upload(file)
                    post.image_url = cloudinary.CloudinaryImage(file).build_url(secure = True)
                    post.save()'''

                cloudinary.config(cloud_name=cloud_name, API_Key=API_Key, API_Secret=API_Secret)
                cloudinary.uploader.upload(pat)
                post.image_url = cloudinary.utils.cloudinary_url(pat)
                post.save()



                return redirect('/feed/')

        else:
            form = Post_form()
        return render(request, 'post.html', {'form': form})
    else:
        return redirect('/login/')


def feed_view(request):
    return render(request,'feed.html')


def failure_view(request):
    return render(request,'failure.html')


# For validating the session
def check_validation(request):
    if request.COOKIES.get('session_token'):
        session = SessionToken.objects.filter(session_token = request.COOKIES.get('session_token')).first()
        if session:
            time_to_live = session.created_on + timedelta(days=1)
            if time_to_live > timezone.now():
                return session.user
    else:
        return None





def upload(file, cloud_name, API_Key, API_Secret):
    cloudinary.config(cloud_name=cloud_name, API_Key=API_Key, API_Secret=API_Secret)

    cloudinary.uploader.upload(file)


