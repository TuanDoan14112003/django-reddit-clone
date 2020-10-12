from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Room(models.Model):
    """Represents chat rooms that users can join"""
    members = models.ManyToManyField(User)
    ssid = models.CharField(max_length=130,null=True,blank=True)
    def get_absolute_url(self):
        return reverse('room_detail', kwargs={'slug': self.slug})