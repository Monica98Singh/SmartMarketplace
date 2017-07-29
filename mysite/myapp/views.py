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

from clarifai import rest
from clarifai.rest import ClarifaiApp

'''import cloudinary
import cloudinary.api
import cloudinary.uploader
'''
import base64

# Create your views here.
from django.utils.datetime_safe import datetime

# Write your keys and api_secret by defining them here

clarifi_api_key = " "

imgur_CLIENT_ID = " "
imgur_CLIENT_SECRET = " "

sendgrid_API_KEY = " "




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
                #result_list = []
                #length = len(result['outputs'][0]['data']['concepts'])
                #for x in range(0, length):
                 #   a = result['outputs'][0]['data']['concepts'][x]['name']
                  #  result_list = result_list.append(a)

                client = ImgurClient(imgur_CLIENT_ID, imgur_CLIENT_SECRET)
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
        a = PostModel.objects.all()

        for post in posts:
            existing_like = LikeModel.objects.filter(id=post.id, user=user).first()
            if existing_like:
                post.has_liked = True
        #import pdb;pdb.set_trace()

            path = os.path.join(BASE_DIR, post.image.url)
            if post.image_url:
                if post.image_url is not None:
                    app = ClarifaiApp(api_key=clarifi_api_key)

                    # get the general model
                    model = app.models.get("general-v1.3")

                    # predict with the model
                    response = model.predict_by_url(url=post.image_url)
                    post.category = response['outputs'][0]['data']['concepts'][0]['name']
                    post.save()
                else:
                    pass


        return render(request, 'feed.html', {'posts': posts})
    else:

        return redirect('/login/')


def like_view(request):   # view created for liking a post
    user = check_validation(request)    # check if user session exists

    if user and request.method == 'POST':
        form = Like_form(request.POST)
        if form.is_valid(): # check if form is valid or not
            post_id = form.cleaned_data.get('post').id  # retrieve post id of the post liked
            a = PostModel.objects.filter(id=post_id)    # get PostModel object with post id of the post which is liked
            b = a[0].user   # accessing user attribute of PostModel object a
            c = b.email     # accessing email of the creator of that post which is liked
            d = user.username   # accessing username of the creator of that post which is liked
            e = str(a[0].image) # get the name of the image which is liked
            existing_like = LikeModel.objects.filter(post_id=post_id, user=user).first()    # checking like on the post
            if not existing_like:
                LikeModel.objects.create(post_id=post_id, user=user)    # creating like on the post
                sg = sendgrid.SendGridAPIClient(apikey=sendgrid_API_KEY)     # sending email to creator of post informing
                                                                    # their post is liked using sendgrid
                from_email = Email("smartmarketplace@gmail.com")
                to_email = Email(c)
                subject = "Liked your post"
                content = Content("text/plain", "Your post " + e + " on Smart P2P MarketPlace Website is liked by " + d)
                mail = Mail(from_email, subject, to_email, content)
                response = sg.client.mail.send.post(request_body=mail.get())
            else:
                existing_like.delete()  # if like exists delete it then
            return redirect('/feed/')   # redirect to feeds page after liking or deleting like on a post
    else:
        return redirect('/login/')  # if user session not exists, redirect to login page


def comment_view(request):  # view for making comment on post
    user = check_validation(request)    # check if user session exists or not

    if user and request.method == 'POST':
        form = Comment_form(request.POST)
        if form.is_valid():     # check if form is valid
            post_id = form.cleaned_data.get('post').id
            comment_text = form.cleaned_data.get('comment_text')
            comment = CommentModel.objects.create(user=user, post_id=post_id, comment_text=comment_text)
            comment.save()  # comment saved in database

            a = CommentModel.objects.filter(id=post_id)  # get PostModel object with post id of the post which is liked
            b = a[0].user  # accessing user attribute of CommentModel object a
            c = b.email  # accessing email of the creator of that post on which comment is made
            d = user.username  # accessing username of the creator of that post on which comment is made
            e = str(a[0].comment_text)  # get the comment made on the post
            f = str(b.image)

            sg = sendgrid.SendGridAPIClient(apikey=sendgrid_API_KEY)  # sending email to creator of post informing
            # their post is liked using sendgrid
            from_email = Email("smartmarketplace@gmail.com")
            to_email = Email(c)
            subject = "comment on your post"
            content = Content("text/plain", "The comment " + e + " is made on your post " + f + " on Smart P2P MarketPlace Website by " + d)
            mail = Mail(from_email, subject, to_email, content)
            response = sg.client.mail.send.post(request_body=mail.get())
            return redirect('/feed/')   # user redirected to feeds page after making comment
        else:
            return redirect('/feed/')   # if form not valid,redirect user to feed page
    else:
        return redirect('/login/')  # if user session does not exist, redirected to login page


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


