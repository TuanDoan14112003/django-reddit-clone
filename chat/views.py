from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import ChatGrant
from twilio.rest import Client
from django.conf import settings
from channels.layers import get_channel_layer
from .models import Room
from asgiref.sync import async_to_sync
from notification.models import CustomNotification
from notification.serializers import NotificationSerializer
import json
from django.contrib.auth.decorators import login_required


@login_required
def room_detail(request):
    user = request.user
    rooms = Room.objects.filter(members=user)
    context = {'rooms':[]}
    for room in rooms:
        for mem in room.members.all():
            if mem != request.user:
                the_other_member = mem
                break
        context['rooms'].append({'the_other_member':the_other_member,'room':room})
    print(context)
    notifications = request.user.notifications.order_by('-timestamp')
    context['notifications'] = notifications
    context['unread_notifications'] = len(request.user.notifications.filter(unread=True))
    return render(request, 'chat/chat.html',context)


def token(request):
    print('vao token roi')
    identity = request.GET.get('identity', request.user.username)
    device_id = request.GET.get('device', 'default')  # unique device ID

    account_sid = settings.TWILIO_ACCOUNT_SID
    api_key = settings.TWILIO_API_KEY
    api_secret = settings.TWILIO_API_SECRET
    chat_service_sid = settings.TWILIO_CHAT_SERVICE_SID

    token = AccessToken(account_sid, api_key, api_secret, identity=identity)

    # Create a unique endpoint ID for the device
    endpoint = "MiniSlackChat:{0}:{1}".format(identity, device_id)

    if chat_service_sid:
        chat_grant = ChatGrant(endpoint_id=endpoint,
                               service_sid=chat_service_sid)
        token.add_grant(chat_grant)

    response = {
        'identity': identity,
        'token': token.to_jwt().decode('utf-8')
    }

    return JsonResponse(response)

def check_room(request):
    u1_username = request.POST.get('u1')
    u2_username = request.POST.get('u2')
    u1 = User.objects.get(username=u1_username)
    u2 = User.objects.get(username=u2_username)
    room_exists = Room.objects.filter(members=u1).filter(members=u2).exists()
    print(room_exists)
    if room_exists:
        is_new_room = False
    else:
        room = Room()
        room.save()
        room.members.add(u1)
        room.members.add(u2)
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        channel = client.chat.services(settings.TWILIO_CHAT_SERVICE_SID) \
                     .channels \
                     .create(type='private')
        room.ssid = channel.sid
        channel.members.create(identity=u1.username)
        channel.members.create(identity=u2.username)
        room.save()
        is_new_room = True
    return JsonResponse({'is_new_room':is_new_room})
    
@login_required
def send_message_notification(request):
    notification = CustomNotification.objects.create(type="comment", recipient=recipient, actor=actor, verb='has sent you a message')
    channel_layer = get_channel_layer()
    channel = "comment_like_notifications_{}".format(recipient.username)
    print(json.dumps(NotificationSerializer(notification).data))
    async_to_sync(channel_layer.group_send)(
        channel, {
            "type": "notify",
            "command": "new_like_comment_notification",
            "notification": json.dumps(NotificationSerializer(notification).data)
        }
    )