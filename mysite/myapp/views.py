# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta
from django.shortcuts import render, redirect
from django.utils import timezone

from forms import Signup_form, Login_form, Post_form, Like_form, Comment_form
from models import UserModel, SessionToken, PostModel, LikeModel, CommentModel
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password
#from imgurpython import ImgurClient
from mysite.settings import BASE_DIR
import re
'''import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()'''
import os
from imgurpython import ImgurClient

import sendgrid
from sendgrid.helpers.mail import *

'''import cloudinary
import cloudinary.api
import cloudinary.uploader
'''



# Create your views here.
from django.utils.datetime_safe import datetime

'''for imgur'''
CLIENT_ID = 'ff5b64065fa26a5'
CLIENT_SECRET = '4d3de558e74f2537d5b74bba32ebe470bfbad933'

'''API_Key = '564665283213574'
API_Secret = 'I35M1dR4ztrh8bJoG3OZ0nGEfQ4'
cloud_name = 'acadview'''

'''for sendgrid'''
API_KEY = "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"




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
                post.save()

                path = os.path.join(BASE_DIR, post.image.url)

                client = ImgurClient(CLIENT_ID, CLIENT_SECRET)
                post.image_url = client.upload_from_path(path, anon=True)['link']
                post.save()

                return redirect('/feed/')

        else:
            form = Post_form()
        return render(request, 'post.html', {'form': form})
    else:
        return redirect('/login/')


def feed_view(request):
    user = check_validation(request)
    if user:

        posts = PostModel.objects.all().order_by('-created_on')
        for post in posts:
            existing_like = LikeModel.objects.filter(post_id=post.id, user=user).first()
            if existing_like:
                post.has_liked = True

        return render(request, 'feed.html', {'posts': posts})
    else:

        return redirect('/login/')


def like_view(request):
    user = check_validation(request)

    if user and request.method == 'POST':
        form = Like_form(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            a = PostModel.objects.filter(id=post_id)
            b = a[0].user
            c = b.email
            d = user.username
            e = str(a[0].image)
            existing_like = LikeModel.objects.filter(post_id=post_id, user=user).first()
            if not existing_like:
                LikeModel.objects.create(post_id=post_id, user=user)
                sg = sendgrid.SendGridAPIClient(apikey=API_KEY)
                from_email = Email("smartmarketplace@gmail.com")
                to_email = Email(c)
                subject = "Liked your post"
                content = Content("text/plain", "Your post " + e + " on Smart P2P MarketPlace Website is liked by " + d)
                mail = Mail(from_email, subject, to_email, content)
                response = sg.client.mail.send.post(request_body=mail.get())
            else:
                existing_like.delete()
            return redirect('/feed/')
    else:
        return redirect('/login/')


def comment_view(request):
    user = check_validation(request)

    if user and request.method == 'POST':
        form = Comment_form(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            comment_text = form.cleaned_data.get('comment_text')
            comment = CommentModel.objects.create(user=user, post_id=post_id, comment_text=comment_text)
            comment.save()
            return redirect('/feed/')
        else:
            return redirect('/feed/')
    else:
        return redirect('/login/')


def failure_view(request):
    return render(request, 'failure.html')


# For validating the session
def check_validation(request):
    if request.COOKIES.get('session_token'):
        session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
        if session:
            time_to_live = session.created_on + timedelta(days=1)
            if time_to_live > timezone.now():
                return session.user
    else:
        return None





'''def upload(file, cloud_name, API_Key, API_Secret):
    cloudinary.config(cloud_name=cloud_name, API_Key=API_Key, API_Secret=API_Secret)

    cloudinary.uploader.upload(file)'''


