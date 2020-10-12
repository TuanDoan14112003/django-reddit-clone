"""django_reddit URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from post.views import PostListHomePage,SubredditCreateView, PostCreateView, PostListUser ,PostListSubreddit, PostDetailView, post_comment, vote, join_subreddit, ReadAllNotification
from notification.views import get_notification
from user.views import register, ProfileEdit,loginPage
from chat.views import room_detail,check_room,token,send_message_notification
from django.contrib.auth.views import LoginView,LogoutView
from django_reddit import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', PostListHomePage, name='homepage'),
    path('subreddit/new/', SubredditCreateView.as_view(template_name='post/subreddit_form.html'), name='subreddit-create'),
    path('subreddit/<int:pk>/', PostListSubreddit, name='subreddit-detail'),
    path('subreddit/<int:pk>/new-post',PostCreateView.as_view(),name='create-post'),
    path('post/<int:pk>/', PostDetailView, name='post-detail'),
    path('post/new_comment/', post_comment, name='comment-create'),
    path('vote/',vote,name = 'vote'),
    path('user/<str:pk>', PostListUser, name='profile'),
    path('notifications/',get_notification, name='notifications'),
    path('register/', register, name='register'),
    path('login/', loginPage, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('subreddit/<int:subreddit_id>/join_sub/',join_subreddit,name='join-subreddit'),
    path('read-all-notification/',ReadAllNotification,name='read-all-notification'),
    path('profile/edit',ProfileEdit, name='edit'),
    path('chat/',room_detail, name='chat'),
    path('check-room/',check_room,name='check-room'),
    path('token/',token,name='token'),
    path('send-message-notifcation/',send_message_notification,name='send-message-notification')
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
