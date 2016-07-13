from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.conf import settings
from allauth.account.models import EmailAddress
from allauth.account.signals import user_signed_up, user_logged_in

class Avatar(models.Model):
    avatar_raw = models.ImageField("User upload avatar", upload_to='upload/%Y%m%d', blank=False, null=False, default="")
    avatar_l = models.ImageField("large avatar", upload_to='avatar/%Y%m%d', blank=False, null=False, default="")
    avatar_m = models.ImageField("medium avatar", upload_to='avatar/%Y%m%d', blank=False, null=False, default="")
    avatar_s = models.ImageField("small avatar", upload_to='avatar/%Y%m%d', blank=False, null=False, default="")
    deleted = models.BooleanField(default=False)

class UserProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True, verbose_name='user', related_name='profile')
    oauth = models.CharField(max_length=16, blank=True, null=True)
    display_name = models.CharField(max_length=256, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=256, blank=True, null=True)
    company = models.CharField(max_length=256, blank=True, null=True)
    email = models.EmailField('email address', blank=True)
    description = models.CharField(max_length=256, blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    gitlab = models.URLField(blank=True, null=True)
    profile_init_reward = models.BooleanField(default=False)
    last_modified = models.DateTimeField(auto_now=True, blank=True, null=True)
    avatar = models.ForeignKey(Avatar, on_delete=models.PROTECT, blank=True, null=True)
    reputation = models.IntegerField(default=0)
    following = models.ManyToManyField('UserProfile', blank=True, related_name='follower')
    has_notification = models.BooleanField(default=False)
    
    def __unicode__(self):
        return "{}'s profile".format(self.user.username)
    
    class Meta:
        db_table = 'user_profile'
    
    def has_avatar(self):
        if self.avatar:
            return True
        else:
            return False
    
    def can_create_topic(self):
        return self.reputation >= settings.REP_NEED_SETTING[settings.USER_CREATE_TOPIC]
    
    def can_create_tool(self):
        return self.reputation >= settings.REP_NEED_SETTING[settings.USER_CREATE_TOOL]

class ReputationStat(models.Model):
    user = models.ForeignKey(User, related_name='repu_stat')
    date = models.DateTimeField(auto_now=True, blank=False, null=False)
    stat_type = models.IntegerField()
    amount = models.IntegerField(blank=False, null=False)
    total = models.IntegerField(blank=False, null=False)
    topic_id = models.IntegerField(blank=True, null=True)
    node_id = models.IntegerField(blank=True, null=True)

class Notification(models.Model):
    user = models.ForeignKey(User, related_name='notifications')
    date = models.DateTimeField(auto_now=True, blank=False, null=False, db_index=True)
    detail = models.TextField(blank=False, null=False)
    read = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    
    class Meta():
        ordering = ['-date']

@receiver(user_signed_up)
def set_initial_user_profile(request, user, sociallogin=None, **kwargs):
    if sociallogin:
        oauth = sociallogin.account.provider
        if oauth == 'github':
            name = sociallogin.account.extra_data['name']
            location = sociallogin.account.extra_data['location']
            company = sociallogin.account.extra_data['company']
            github = sociallogin.account.extra_data['html_url']
            blog = sociallogin.account.extra_data['blog']
            bio = sociallogin.account.extra_data['bio']
            
            profile = UserProfile(user=user, oauth=oauth, display_name=name, location=location,
                                  company=company, github=github, website=blog, description=bio)
        elif oauth == 'google':
            name = sociallogin.account.extra_data['name']
            
            profile = UserProfile(user=user, oauth=oauth, display_name=name)
    else:
        profile = UserProfile(user=user)
    
    profile.save()

@receiver(user_logged_in)
def check_profile(request, user, sociallogin=None, **kwargs):
    try:
        user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile(user=user)
        profile.save()

