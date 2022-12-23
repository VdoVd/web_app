from django.db import models

class User(models.Model):
    username=models.CharField(max_length=20,unique=True)
    password=models.CharField(max_length=20)
    mobile=models.CharField(max_length=11,unique=True)