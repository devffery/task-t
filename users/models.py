from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        username = extra_fields.pop('username', email)  # Use email as username by default
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class CustomUser(AbstractUser):
    userId = models.CharField(max_length=50, unique=True, null=False, default=uuid.uuid4 )
    firstName = models.CharField(max_length=250, null=False)
    lastName = models.CharField(max_length=250, null=False)
    email = models.EmailField(max_length=250, unique=True, null=False)
    phone = models.CharField(max_length=20)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstName', 'lastName'] 

    def save(self, *args, **kwargs):
        if not self.pk and not self.username:
            self.username = self.email
        super().save(*args, **kwargs)       

class Organisation(models.Model):
    orgId = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=250, null=False)
    description = models.TextField(null=True)
    users = models.ManyToManyField(CustomUser, related_name='organisations')

    def __str__(self):
        return self.name
