"""niuforum URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
import niuauth.views
import forum.views

urlpatterns = [
    url(r'^$', forum.views.forum_index, name='forum_index'),
    url(r'^s/(?P<filter>\w{0,10})/$', forum.views.forum_index, name='forum_index'),
    
    url(r'^n/(?P<node_id>\d+)/$', forum.views.node_view, name='node_view'),
    url(r'^n/(?P<node_id>\d+)/(?P<filter>\w{0,10})/$', forum.views.node_view, name='node_view'),
    url(r'^t/(?P<topic_id>\d+)/$', forum.views.topic_view, name='topic_view'),
    url(r'^t/(?P<topic_id>\d+)/reply/$', forum.views.reply_topic_view, name='reply_topic_view'),
    
    url(r'^topics/add/$', forum.views.create_topic_view, name='create_topic_view'),
    url(r'^topics/add/(?P<node_id>\d+)/$', forum.views.create_topic_view, name='create_topic_view'),
    url(r'^topics/update/(?P<topic_id>\d+)/$', forum.views.update_topic_view, name='update_topic_view'),
    
    url(r'^action/watch-node/(?P<node_id>\d+)/$', forum.views.watch_node_view, name='watch_node_view'),
    url(r'^action/like-topic/(?P<topic_id>\d+)/$', forum.views.like_topic_view, name='like_topic_view'),
    url(r'^action/render/$', forum.views.render_markdown_view, name='render_markdown_view'),
    
    url(r'^user/(?P<user_id>\w{0,50})/$', niuauth.views.user_profile, name='user_profile'),
    url(r'^user/(?P<user_id>\w{0,50})/topic/$', niuauth.views.user_topic, name='user_topic'),
    
    url(r'^settings/profile/$', niuauth.views.settings_profile, name='settings_profile'),
    url(r'^notification/$', niuauth.views.notification_view, name='notification_view'),
    url(r'^notification/clear/$', niuauth.views.clear_notification_view, name='clear_notification_view'),
    
    url(r'^accounts/', include('allauth.urls')),
    url(r'^admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
