from django.db.models.signals import post_save
from django.contrib.auth.models import User
from .models import Subreddit
from django.dispatch import receiver



@receiver(post_save, sender=Subreddit)
def create_vote(sender, instance, created, **kwargs):
    if created:
        instance.users.add(instance.creator)


