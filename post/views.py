from django.views.generic import (
    CreateView
)
from django.contrib.auth.mixins import LoginRequiredMixin


from .models import Post,Vote,Comment,Subreddit
from user.models import Profile
from django.contrib.auth.models import User
from notification.models import CustomNotification
from notification.serializers import NotificationSerializer


from django.shortcuts import render,get_object_or_404
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.decorators import login_required
from django.middleware.csrf import get_token
from django.urls import reverse
from django.http import JsonResponse, HttpResponseBadRequest, Http404, HttpResponseForbidden
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
# Create your views here.


#==================================================Helper functions==========================================================================#
def post_only(func):# pragma: no cover
    def decorated(request, *args, **kwargs):
        if request.method != 'POST':
            return HttpResponseNotAllowed(['GET'])
        return func(request, *args, **kwargs)
    return decorated



def create_new_notification(recipient,actor,verb,post):
    notification = CustomNotification.objects.create(type="comment", recipient=recipient, profile=actor.profile, actor=actor, verb=verb,post=post)
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
#==================================================End Helper functions==========================================================================#

@login_required
def post_comment(request):
    parent_type = request.POST.get('parentType', None)
    parent_id = request.POST.get('parentId', None)
    raw_comment = request.POST.get('commentContent', None)
    if not all([parent_id, parent_type]) or \
            parent_type not in ['comment', 'post'] or \
        not parent_id.isdigit():
        return HttpResponseBadRequest()
    if not raw_comment:
        return JsonResponse({'msg': "You have to write something."})
    author = request.user
    parent_object = None
    
    try:  # try and get comment or submission we're voting on
        if parent_type == 'comment':
            parent_object = Comment.objects.get(id=parent_id)
        elif parent_type == 'post':
            parent_object = Post.objects.get(id=parent_id)

    except (Comment.DoesNotExist, Post.DoesNotExist):
        return HttpResponseBadRequest()
    
    comment = Comment.create(author=author,
                             raw_comment=raw_comment,
                             parent=parent_object)
    comment.save()
    post = comment.post
    new_comment_html = f""" 
    <li>
            <form class="comment-voting d-flex flex-column"
            data-what-type="comment"
            data-what-id="{comment.id}">
            <input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">
            <button type="button"><i title="upvote" onclick="vote(this)" class="fas fa-arrow-alt-circle-up"></i></button>
            <button type="button"><i title="downvote" onclick="vote(this)" class="fas fa-arrow-alt-circle-down"></i></button>
            </form>
            <div class="comment-details d-flex justify-content-start">
                <a href="/user/{request.user.id}"><p class="comment-user-name">u/{request.user.username}</p></a>
                <p class="score comment-points">0 points</p>
                <p class="comment-time">just now</p>
            </div>
            <div class="comment-content text-left">
                {raw_comment}
            </div>
            <div class="comment-interaction d-flex justify-content-start">
                <button class="reply-button" onclick="displayHideForm(this.parentElement.parentElement)">
                    <i class="fas fa-comment-alt"></i> 
                    <span>Reply</span>
                </button>
            </div>
            <div class="col-12 container-fluid individual-reply">
                <div class="row">
                    <form class="reply_form" class=" col-12 d-flex flex-column"
                    data-parent-type="comment"
                    data-parent-id="{comment.id}">
                        <textarea class="comment_form" type="text" class="p-1 mt-1" placeholder="What are your thoughts"></textarea>
                        <button class="btn btn-primary ml-auto mt-3"><span>Comment</span></button>
                    </form>
                </div>
            </div>
            <ul class="child_comments" comment_id="{comment.id}">
            </ul>
    </li>
    """
    if request.user != post.author:
        if parent_type == 'post':
            create_new_notification(recipient=post.author,actor=request.user,verb="commented on your post",post=post)
        elif parent_type == 'comment':
            if parent_object.author == post.author:
                create_new_notification(recipient=post.author,actor=request.user,verb="replied your comment",post=post)
            else:
                create_new_notification(recipient=post.author,actor=request.user,verb="commented on your post")
                create_new_notification(recipient=parent_object.author,actor=request.user,verb="replied your comment",post=post)
    else:
        if parent_type == 'comment':
            if parent_object.author != post.author:
                create_new_notification(recipient=parent_object.author,actor=request.user,verb="replied your comment",post=post)

    return JsonResponse({'new_comment_html':new_comment_html})

@login_required
def ReadAllNotification(request):
    user = request.user
    user.notifications.filter(unread=True).update(unread=False)
    user.save()
    return JsonResponse({'msg':'success'})



def PostListHomePage(request):
    post_list = Post.objects.all().order_by('-date_posted')
    page = request.GET.get('page', 1)
    paginator = Paginator(post_list, 2)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    post_votes = {}
    notifications = {}
    context = {'posts' : posts}
    if request.user.is_authenticated:
        for post in post_list:
            try:
                vote = Vote.objects.get(
                    vote_object_type=post.get_content_type(),
                    vote_object_id=post.id,
                    user=request.user)
                post_votes[post.id] = vote.value
            except Vote.DoesNotExist:
                pass
        subreddits = Subreddit.objects.all().order_by('-member_count')
        notifications = request.user.notifications.order_by('-timestamp')
        context['post_votes'] = post_votes
        context['notifications'] = notifications
        context['unread_notifications'] = len(request.user.notifications.filter(unread=True))
        context['subreddits'] = subreddits
    return render(request, 'post/homepage.html', context)



@post_only
@login_required
def vote(request):
    # The type of object we're voting on, can be 'submission' or 'comment'
    vote_object_type = request.POST.get('what', None)

    # The ID of that object as it's stored in the database, positive int
    vote_object_id = request.POST.get('what_id', None)

    # The value of the vote we're writing to that object, -1 or 1
    # Passing the same value twice will cancel the vote i.e. set it to 0
    new_vote_value = request.POST.get('vote_value', None)

    # By how much we'll change the score, used to modify score on the fly
    # client side by the javascript instead of waiting for a refresh.
    vote_diff = 0

    if not request.user.is_authenticated:
        return HttpResponseForbidden()
    else:
        user = request.user

    try:  # If the vote value isn't an integer that's equal to -1 or 1
        # the request is bad and we can not continue.
        new_vote_value = int(new_vote_value)

        if new_vote_value not in [-1, 1]:
            raise ValueError("Wrong value for the vote!")

    except (ValueError, TypeError):
        return HttpResponseBadRequest()

    # if one of the objects is None, 0 or some other bool(value) == False value
    # or if the object type isn't 'comment' or 'submission' it's a bad request
    if not all([vote_object_type, vote_object_id, new_vote_value]) or \
            vote_object_type not in ['comment', 'post']:
        return HttpResponseBadRequest()

    # Try and get the actual object we're voting on.
    try:
        if vote_object_type == "comment":
            vote_object = Comment.objects.get(id=vote_object_id)

        elif vote_object_type == "post":
            vote_object = Post.objects.get(id=vote_object_id)
        else:
            return HttpResponseBadRequest()  # should never happen

    except (Comment.DoesNotExist, Post.DoesNotExist):
        return HttpResponseBadRequest()

    # Try and get the existing vote for this object, if it exists.
    try:
        vote = Vote.objects.get(vote_object_type=vote_object.get_content_type(),
                                vote_object_id=vote_object.id,
                                user=user)
    except Vote.DoesNotExist:
        # Create a new vote and that's it.
        vote = Vote.create(user=user,
                           vote_object=vote_object,
                           vote_value=new_vote_value)
        vote.save()
        vote_diff = new_vote_value
        return JsonResponse({'error'   : None,
                             'voteDiff': vote_diff})

    # User already voted on this item, this means the vote is either
    # being canceled (same value) or changed (different new_vote_value)
    if vote.value == new_vote_value:
        # canceling vote
        vote_diff = vote.cancel_vote()
        if not vote_diff:
            return HttpResponseBadRequest(
                'Something went wrong while canceling the vote')
    else:
        # changing vote
        vote_diff = vote.change_vote(new_vote_value)
        if not vote_diff:
            return HttpResponseBadRequest(
                'Wrong values for old/new vote combination')

    return JsonResponse({'error'   : None,
                         'voteDiff': vote_diff})


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content','image']

    def form_valid(self, form):
        subreddit = Subreddit.objects.get(id=self.kwargs['pk'])
        form.instance.subreddit = subreddit
        form.instance.author = self.request.user
        return super().form_valid(form)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        notifications = self.request.user.notifications.order_by('-timestamp')
        context['notifications'] = notifications
        context['unread_notifications'] =len(self.request.user.notifications.filter(unread=True))
        return context


#==================================================Subreddit==========================================================================#

class SubredditCreateView(LoginRequiredMixin,CreateView):
    model = Subreddit
    fields = ['name','description','cover', 'avatar']

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        notifications = self.request.user.notifications.order_by('-timestamp')
        context['notifications'] = notifications
        context['unread_notifications'] =len(self.request.user.notifications.filter(unread=True))
        return context

def PostListSubreddit(request,pk):
    subreddit = Subreddit.objects.get(id=pk)
    post_list = Post.objects.filter(subreddit=subreddit).order_by('-date_posted')
    page = request.GET.get('page', 1)
    paginator = Paginator(post_list, 2)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    post_votes = {}
    notifications = {}
    join = None
    context = {'posts':posts,'subreddit': subreddit}
    if request.user.is_authenticated:
        for post in post_list:
            try:
                vote = Vote.objects.get(
                    vote_object_type=post.get_content_type(),
                    vote_object_id=post.id,
                    user=request.user)
                post_votes[post.id] = vote.value
            except Vote.DoesNotExist:
                pass
        notifications = request.user.notifications.order_by('-timestamp')
        join = subreddit.users.filter(id=request.user.id).exists()
        context['post_votes'] = post_votes
        context['notifications'] = notifications
        context['unread_notifications'] =len(request.user.notifications.filter(unread=True))
        context['not_join'] = not join
    return render(request, 'post/subreddit_detail.html', context)


def PostListUser(request,pk):
    user = User.objects.get(id=pk)
    post_list = Post.objects.filter(author=user).order_by('-date_posted')
    page = request.GET.get('page', 1)
    paginator = Paginator(post_list, 2)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    post_votes = {}
    notifications = {}
    context = {
        'posts': posts,
    }
    if request.user.is_authenticated:
        for post in post_list:
            try:
                vote = Vote.objects.get(
                    vote_object_type=post.get_content_type(),
                    vote_object_id=post.id,
                    user=request.user)
                post_votes[post.id] = vote.value
            except Vote.DoesNotExist:
                pass
        notifications = request.user.notifications.order_by('-timestamp')
        context['post_votes'] = post_votes
        context['notifications'] = notifications
        context['unread_notifications'] = len(request.user.notifications.filter(unread=True))
    context['user_profile'] = user
    return render(request, 'user/profile.html', context)


def PostDetailView(request, pk=None):  
    this_post = get_object_or_404(Post, id=pk)
    thread_comments = Comment.objects.filter(post=this_post)
    context = {'object'   : this_post,
               'comments'     : thread_comments,}
    if request.user.is_authenticated:
        try:
            reddit_user = request.user
        except User.DoesNotExist:
            reddit_user = None
    else:
        reddit_user = None

    post_vote_value = None
    comment_votes = {}

    if reddit_user:
        try:
            vote = Vote.objects.get(
                vote_object_type=this_post.get_content_type(),
                vote_object_id=this_post.id,
                user=reddit_user)
            post_vote_value = vote.value
        except Vote.DoesNotExist:
            pass

        try:
            user_thread_votes = Vote.objects.filter(user=reddit_user,
                                                    post=this_post)
            for vote_item in user_thread_votes:
                print(vote_item.vote_object.id)
                comment_votes[vote_item.vote_object.id] = vote_item.value
        except:
            pass
        notifications = request.user.notifications.order_by('-timestamp')
        context['comment_votes'] = comment_votes
        context['notifications'] = notifications
        context['post_vote_value'] = post_vote_value
        context['unread_notifications'] = len(request.user.notifications.filter(unread=True))
    return render(request, 'post/post_detail.html',context)
                        
@login_required
def join_subreddit(request,subreddit_id):
    if request.method == 'POST':
        try:
            sub = Subreddit.objects.get(id=subreddit_id)
            sub.users.add(request.user)
            sub.member_count += 1
            sub.save()
            print(sub.users.all())
            return JsonResponse({'msg':'success'})
        except:
            return JsonResponse({'msg':'fail'})

   
