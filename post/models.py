from django.db import models
from django.contrib.auth.models import User

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from mptt.models import MPTTModel, TreeForeignKey
from django_reddit.utils.model_utils import ContentTypeAware, MttpContentTypeAware


from django.utils import timezone
import mistune
from django.urls import reverse
from PIL import Image
# Create your models here.

class Subreddit(models.Model):
    name = models.CharField(max_length=50,unique=True)
    users = models.ManyToManyField(User,related_name='%(class)s_member_of')
    creator = models.ForeignKey(User,on_delete=models.CASCADE,related_name='%(class)s_creator_of')
    cover = models.ImageField(default='default.jpg', upload_to='subreddit_pics')
    avatar = models.ImageField(default='default.jpg', upload_to='subreddit_pics')
    description = models.TextField(null=True)
    member_count = models.IntegerField(blank=True,null=True,default=1)
    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse('subreddit-detail', kwargs={'pk': self.pk})


class Post(ContentTypeAware):
    title = models.CharField(max_length=100)
    content = models.TextField(null=True,blank=True)
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    ups = models.IntegerField(default=0)
    downs = models.IntegerField(default=0)
    subreddit = models.ForeignKey(Subreddit, on_delete=models.CASCADE,null=True)
    comment_count = models.PositiveSmallIntegerField(default=0)
    image = models.ImageField(upload_to='post_pics',null=True,blank=True)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})

class Comment(MttpContentTypeAware):
    author = models.ForeignKey(User,on_delete=models.CASCADE)
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name="comments")
    parent = TreeForeignKey('self', related_name='children',
                            null=True, blank=True, db_index=True,on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    ups = models.IntegerField(default=0)
    downs = models.IntegerField(default=0)
    score = models.IntegerField(default=0)
    raw_comment = models.TextField(blank=True)
    html_comment = models.TextField(blank=True)

    class MPTTMeta:
        order_insertion_by = ['-score']

    @classmethod
    def create(cls, author, raw_comment, parent):
        """
        Create a new comment instance. If the parent is submisison
        update comment_count field and save it.
        If parent is comment post it as child comment
        :param author: RedditUser instance
        :type author: RedditUser
        :param raw_comment: Raw comment text
        :type raw_comment: str
        :param parent: Comment or Post that this comment is child of
        :type parent: Comment | Post
        :return: New Comment instance
        :rtype: Comment
        """

        html_comment = mistune.markdown(raw_comment)
        # todo: any exceptions possible?
        comment = cls(author=author,
                      raw_comment=raw_comment,
                      html_comment=html_comment)

        if isinstance(parent, Post):
            post = parent
            comment.post = post
        elif isinstance(parent, Comment):
            post = parent.post
            comment.post = post
            comment.parent = parent
        else:
            return
        post.comment_count += 1
        post.save()

        return comment

    def __unicode__(self):
        return "<Comment:{}>".format(self.id)


class Vote(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    post = models.ForeignKey(Post,on_delete=models.CASCADE)
    vote_object_type = models.ForeignKey(ContentType,on_delete=models.CASCADE)
    vote_object_id = models.PositiveIntegerField()
    vote_object = GenericForeignKey('vote_object_type', 'vote_object_id')
    value = models.IntegerField(default=0)

    @classmethod
    def create(cls, user, vote_object, vote_value):
        """
        Create a new vote object and return it.
        It will also update the ups/downs/score fields in the
        vote_object instance and save it.

        :param user: RedditUser instance
        :type user: RedditUser
        :param vote_object: Instance of the object the vote is cast on
        :type vote_object: Comment | Submission
        :param vote_value: Value of the vote
        :type vote_value: int
        :return: new Vote instance
        :rtype: Vote
        """
        if isinstance(vote_object, Post):
            print(vote_value)
            post = vote_object
            vote_object.author.profile.karma += vote_value
        else:
            print(vote_value)
            post = vote_object.post
            vote_object.author.profile.karma += vote_value

        vote = cls(user=user,
                   vote_object=vote_object,
                   value=vote_value)

        vote.post = post
        # the value for new vote will never be 0
        # that can happen only when removing up/down vote.
        vote_object.score += vote_value
        if vote_value == 1:
            vote_object.ups += 1
        elif vote_value == -1:
            vote_object.downs += 1
        vote_object.save()
        vote_object.author.save()

        return vote

    def change_vote(self, new_vote_value):
        if self.value == -1 and new_vote_value == 1:  # down to up
            vote_diff = 2
            self.vote_object.score += 2
            self.vote_object.ups += 1
            self.vote_object.downs -= 1
        elif self.value == 1 and new_vote_value == -1:  # up to down
            vote_diff = -2
            self.vote_object.score -= 2
            self.vote_object.ups -= 1
            self.vote_object.downs += 1
        elif self.value == 0 and new_vote_value == 1:  # canceled vote to up
            vote_diff = 1
            self.vote_object.ups += 1
            self.vote_object.score += 1
        elif self.value == 0 and new_vote_value == -1:  # canceled vote to down
            vote_diff = -1
            self.vote_object.downs += 1
            self.vote_object.score -= 1
        else:
            return None

        if isinstance(self.vote_object, Post):
            self.vote_object.author.profile.karma += vote_diff
        else:
            self.vote_object.author.profile.karma += vote_diff

        self.value = new_vote_value
        self.vote_object.save()
        self.vote_object.author.save()
        self.vote_object.author.profile.save()
        self.save()

        return vote_diff

    def cancel_vote(self):
        if self.value == 1:
            vote_diff = -1
            self.vote_object.ups -= 1
            self.vote_object.score -= 1
        elif self.value == -1:
            vote_diff = 1
            self.vote_object.downs -= 1
            self.vote_object.score += 1
        else:
            return None

        if isinstance(self.vote_object, Post):
            self.vote_object.author.profile.karma += vote_diff
        else:
            self.vote_object.author.profile.karma += vote_diff

        self.value = 0
        self.save()
        self.vote_object.save()
        self.vote_object.author.save()
        self.vote_object.author.profile.save()
        return vote_diff


