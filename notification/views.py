from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.
@login_required
def get_notification(request):
    notifications = request.user.notifications.order_by('-timestamp')
    context = {'notifications': notifications}
    context['unread_notifications'] = len(request.user.notifications.filter(unread=True))
    return render(request, 'user/notification.html', context)