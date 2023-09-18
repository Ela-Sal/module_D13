from django.db import models
from django.contrib.auth.models import User

class OneTimeCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=5)
# Create your models here.
