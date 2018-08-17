from __future__ import unicode_literals
from django.db import models
from datetime import datetime
import re

# create a regular expression object that we can use run operations on
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
WORD_SPACE_REGEX = re.compile(r'^[A-Za-z ]+')

class UserManager(models.Manager):
    def basic_validator(slef, postData):
        errors = {}
        # validation for firstname
        if 'first_name' in postData:
            if len(postData['first_name']) == 0:
                errors['first_name'] = "*First Name is required"
            elif len(postData['first_name']) < 3:
                errors['first_name'] = "*Must be more than 2 characters"
            elif not postData['first_name'].isalpha():
                errors['first_name'] = "*Alphabets characters only"
        
        # validation for lastname
        if 'last_name' in postData:
            if len(postData['last_name']) == 0:
                errors['last_name'] = "*Last Name is required"
            elif len(postData['last_name']) < 3:
                errors['last_name'] = "*Must be more than 2 characters"
            elif not postData['last_name'].isalpha():
                errors['last_name'] = "*Alphabets characters only"

        # validation for alias
        if 'alias' in postData:
            if len(postData['alias']) == 0:
                errors['alias'] = "*Alias is required"
            elif len(postData['alias']) < 3:
                errors['alias'] = "*Must be more than 2 characters"
        
        # validation for email
        if 'email' in postData:
            if len(postData['email']) == 0:
                errors['email'] = "*Email is required"
            elif not EMAIL_REGEX.match(postData['email']):
                errors['email'] = "*Invalid email"

        # validation for password
        if 'password' in postData:
            if len(postData['password']) == 0:
                errors['password'] = "*Password is required"
            elif len(postData['password']) < 8:
                errors['password'] = '*Password must be at least 8 characters'
            elif postData['password'] != postData['confirm_password']:
                errors['confirm_password'] = '*Password must be match'
        return errors


class BookManager(models.Manager):
    def basic_validator(slef, postData):
        errors = {}
        # validation for title
        if 'title' in postData:
            if len(postData['title']) == 0:
                errors['title'] = "*Book title is required"
            elif len(postData['title']) < 3:
                errors['title'] = "*Must be more than 2 characters"
            elif not WORD_SPACE_REGEX.match(postData['title']):
                errors['title'] = "*Alphabets characters only"
        
        # validation for author
        if len(postData['author']) == 0:
            errors['author'] = "*Author is required"
        elif len(postData['author_list']) != 0:
            errors['author'] = "*You cannot select two author"
        elif not WORD_SPACE_REGEX.match(postData['author']):
            errors['author'] = "*Alphabets characters only"
    

        # validation for review
        if len(postData['review']) == 0:
            errors['review'] = "*Review is required"

        return errors


class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    objects = UserManager()


class Author(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

class Book(models.Model):
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    author = models.ForeignKey(Author, related_name="books")

    objects = BookManager()

class Review(models.Model):
    review = models.TextField()
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    reviewer = models.ForeignKey(User, related_name="my_reviews")
    book_review = models.ForeignKey(Book, related_name="reviews")