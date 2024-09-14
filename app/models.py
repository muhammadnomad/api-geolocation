from djongo import models
from django.contrib.auth.models import AbstractUser
import jsonfield
from django.utils import timezone


class User(AbstractUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.username

class Technicien(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)

class Localisation(models.Model):
    technicien = models.ForeignKey(Technicien, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    locations = jsonfield.JSONField()