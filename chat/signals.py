from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import ChatGrant

from .models import Room
# @receiver(post_save, sender=Room)
# def create_room(sender, instance, created, **kwargs):
#     if not created:
#         client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
#         channel = client.chat.services(settings.TWILIO_CHAT_SERVICE_SID) \
#                      .channels \
#                      .create(type='private')
#         instance.ssid = channel.sid
#         print('---------------------')
#         print(instance.ssid)

        


