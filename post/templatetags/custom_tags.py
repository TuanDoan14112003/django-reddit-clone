from django.template.defaulttags import register
from post.models import Subreddit
from django.contrib.auth.models import User
@register.filter
def get_item(dict,key):
    try:
        return dict.get(key)
    except:
        pass
