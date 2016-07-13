from django.views.generic.base import TemplateView, View
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.crypto import get_random_string
from django.contrib.auth.models import User
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from niuauth.forms import ProfileForm
from niuauth.models import Avatar
from niuauth.utils import user_reward
from forum.utils import create_thumbnail, get_pagination

@method_decorator(login_required, name='dispatch')
class UserProfileView(TemplateView):
    template_name = "niuauth/home.html"
    
    def get_context_data(self, **kwargs):
        data = super(UserProfileView, self).get_context_data(**kwargs)
        
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, username=user_id)
        user_reply = user.replies.order_by('-date_created').all()
        
        paginator = Paginator(user_reply, 10)
        page = self.request.GET.get('page')
        try:
            replies = paginator.page(page)
        except PageNotAnInteger:
            replies = paginator.page(1)
        except EmptyPage:
            replies = paginator.page(paginator.num_pages)
        
        page_list = get_pagination(replies.number, paginator.num_pages, 2)
        
        data['see_user'] = user
        data['replies'] = replies
        data["page_list"] = page_list
        
        return data

user_profile = UserProfileView.as_view()

@method_decorator(login_required, name='dispatch')
class UserTopicView(TemplateView):
    template_name = "niuauth/user_topic.html"
    
    def get_context_data(self, **kwargs):
        data = super(UserTopicView, self).get_context_data(**kwargs)
        
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, username=user_id)
        user_topics = user.topics.order_by('-date_created').all()
        
        paginator = Paginator(user_topics, 10)
        page = self.request.GET.get('page')
        try:
            topics = paginator.page(page)
        except PageNotAnInteger:
            topics = paginator.page(1)
        except EmptyPage:
            topics = paginator.page(paginator.num_pages)
        
        page_list = get_pagination(topics.number, paginator.num_pages, 2)
        
        data['see_user'] = user
        data['topics'] = topics
        data["page_list"] = page_list
        
        return data

user_topic = UserTopicView.as_view()

@method_decorator(login_required, name='dispatch')
class SettingsProfileView(TemplateView):
    template_name = "niuauth/settings_profile.html"
    
    def get_context_data(self, **kwargs):
        data = super(SettingsProfileView, self).get_context_data(**kwargs)
        
        profile = self.request.user.profile
        default_data = {'display_name': profile.display_name,
                        'description': profile.description,
                        'website': profile.website,
                        'company': profile.company,
                        'email': profile.email,
                        'location': profile.location,
                        'github': profile.github,
                        'gitlab': profile.gitlab
                        }
        form = ProfileForm(self.request.POST or None, self.request.FILES or None, initial=default_data)
        data["form"] = form
        data["avatar"] = profile.avatar
        
        return data
    
    def post(self, request, *args, **kwargs):
        data = self.get_context_data()
        form = data["form"]
        if form.is_valid():
            profile = request.user.profile
            
            avatar = form.cleaned_data['avatar']
            display_name = form.cleaned_data['display_name']
            description = form.cleaned_data['description']
            website = form.cleaned_data['website']
            company = form.cleaned_data['company']
            email = form.cleaned_data['email']
            location = form.cleaned_data['location']
            github = form.cleaned_data['github']
            gitlab = form.cleaned_data['gitlab']
            
            if avatar:
                self._save_avatar(profile, avatar)
            
            if not profile.profile_init_reward:
                if avatar and display_name:
                    user_reward(request.user, settings.REP_USER_INIT)
                    profile.profile_init_reward = True
            
            profile.display_name = display_name
            profile.description = description
            profile.website = website
            profile.company = company
            profile.email = email
            profile.location = location
            profile.github = github
            profile.gitlab = gitlab
            
            profile.save()
            
            return HttpResponseRedirect(reverse('settings_profile'))
        
        return super(TemplateView, self).render_to_response(data)
    
    def _save_avatar(self, profile, image):
        new_name = get_random_string(length=6)
        ext = image.name.split('.')[-1]
        image.name = '%s.%s' % (new_name, ext)
        
        large, medium, small = create_thumbnail(image, new_name, ext)
        a = Avatar(avatar_raw=image, avatar_l=large, avatar_m=medium, avatar_s=small)
        a.save()
        
        if profile.has_avatar():
            profile.avatar.deleted = True
            profile.avatar.save()
        
        profile.avatar = a

settings_profile = SettingsProfileView.as_view()

@method_decorator(login_required, name='dispatch')
class NotificationView(TemplateView):
    template_name = "niuauth/notification.html"
    
    def get_context_data(self, **kwargs):
        data = super(NotificationView, self).get_context_data(**kwargs)
        
        notifications = self.request.user.notifications.all()
        
        paginator = Paginator(notifications, 10)
        page = self.request.GET.get('page')
        try:
            noti_list = paginator.page(page)
        except PageNotAnInteger:
            noti_list = paginator.page(1)
        except EmptyPage:
            noti_list = paginator.page(paginator.num_pages)
        
        page_list = get_pagination(noti_list.number, paginator.num_pages, 2)
        
        data["noti_list"] = noti_list
        data["page_list"] = page_list
        
        profile = self.request.user.profile
        profile.has_notification = False
        profile.save()
        
        return data

notification_view = NotificationView.as_view()

@method_decorator(login_required, name='dispatch')
class ClearNotificationView(View):
    def get(self, request, *args, **kwargs):
        self.request.user.notifications.all().delete()
        
        return HttpResponseRedirect(reverse('notification_view'))

clear_notification_view = ClearNotificationView.as_view()

