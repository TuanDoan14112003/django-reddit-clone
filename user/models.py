from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from PIL import Image
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    cover = models.ImageField(default='default_cover.jpg', upload_to='profile_pics')
    karma = models.IntegerField(default=0)
    timestamp = models.DateTimeField(default=timezone.now,null=True)
    def __str__(self):
        return f'{self.user.username} Profile'
