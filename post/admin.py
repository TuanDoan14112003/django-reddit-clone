from django.contrib import admin
from .models import Vote,Comment,Post,Subreddit
# Register your models here.
admin.site.register(Comment)
admin.site.register(Post)
admin.site.register(Subreddit)
admin.site.register(Vote)