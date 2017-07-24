# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.db import models

from cloudinary.models import CloudinaryField

# Create your models here.


class UserModel(models.Model):  # model for storing details of users in database
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=255)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=50)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


class SessionToken(models.Model):   # model for creating session for a logged in user
    user = models.ForeignKey(UserModel)
    session_token = models.CharField(max_length=255)
    last_request_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)

    def create_token(self):  # create session token
        self.session_token = uuid.uuid4()


class PostModel(models.Model):  # model for storing details of a post made by user
    user = models.ForeignKey(UserModel)
    image = models.FileField(upload_to='user_images')
    #images = CloudinaryField()
    image_url = models.CharField(max_length=255)
    caption = models.CharField(max_length=600)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    category = models.CharField(max_length=100, null=True)
    has_liked = False


    @property
    def like_count(self):
        return len(LikeModel.objects.filter(post=self))

    @property
    def comments(self):
        return CommentModel.objects.filter(post=self).order_by('-created_on')


class LikeModel(models.Model):  # model for storing detail when a a post is liked by user
    user = models.ForeignKey(UserModel)
    post = models.ForeignKey(PostModel)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


class CommentModel(models.Model):   # model for storing detail when comment is made on a post
    user = models.ForeignKey(UserModel)
    post = models.ForeignKey(PostModel)
    comment_text = models.CharField(max_length=500)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

