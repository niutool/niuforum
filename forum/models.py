from django.db import models
from django.contrib.auth.models import User

class Section(models.Model):
    name = models.CharField(max_length=32, unique=True, blank=False, null=False)
    date_created = models.DateTimeField(auto_now_add=True)
    order = models.IntegerField(default=1)
    last_modified = models.DateTimeField(auto_now=True, blank=True, null=True)
    
    class Meta():
        ordering = ['-order']
    
    def __str__(self):
        return self.name

class Node(models.Model):
    section = models.ForeignKey(Section, on_delete=models.PROTECT, related_name='nodes')
    name = models.CharField(max_length=32, unique=True, blank=False, null=False)
    description = models.TextField(blank=False, null=False)
    icon_raw = models.ImageField("Node's icon", upload_to='upload/node/%Y%m%d', blank=True, null=True, default="")
    icon_l = models.ImageField("large icon", upload_to='node/%Y%m%d', blank=True, null=True, default="")
    icon_m = models.ImageField("medium icon", upload_to='node/%Y%m%d', blank=True, null=True, default="")
    icon_s = models.ImageField("small icon", upload_to='node/%Y%m%d', blank=True, null=True, default="")
    order = models.IntegerField(default=0)
    is_trash = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True, blank=True, null=True)
    watcher = models.ManyToManyField(User, blank=True, related_name='watch_nodes')
    
    class Meta():
        ordering = ['section', '-order']
    
    def __str__(self):
        return "%s/%s" % (self.section.name, self.name)
    
    def admin_image(self):
        if self.icon_s:
            return '<img src="/media/%s" width="24" height="24" />' % (self.icon_s)
        else:
            return None
    admin_image.allow_tags = True
    admin_image.short_description = 'Icon'

class Topic(models.Model):
    node = models.ForeignKey(Node, on_delete=models.PROTECT, related_name='topics')
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name='topics')
    title = models.CharField(max_length=128, blank=False, null=False)
    markdown = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    abstract = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True, blank=True, null=True)
    liker = models.ManyToManyField(User, blank=True, related_name='like_topics')
    viewed = models.IntegerField(default=0)
    reply_count = models.IntegerField(default=0)
    last_replied = models.DateTimeField(blank=True, null=True)
    rank = models.IntegerField(default=10)
    reply_reward = models.BooleanField(default=False)
    like_reward = models.BooleanField(default=False)
    admin_star = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    editable = models.BooleanField(default=True)
    
    class Meta():
        ordering = ['-rank', '-date_created']

class Reply(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name='replies')
    markdown = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta():
        ordering = ['date_created']

