import json
from django.views.generic import View
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.text import Truncator
from niuauth.utils import user_reward
from niuauth.models import Notification
from forum.models import Section, Node, Topic, Reply
from forum.forms import TopicForm, ReplyForm
from forum.utils import get_pagination, topic_pagination, get_metioned_user
from forum.mismd import render_markdown
from forum.utils import author_required

class JsonReturn(object):
    J_SUCCESS = 0
    J_REDIRECT = 1
    J_ERROR = 2
    
    def __init__(self):
        self._code = JsonReturn.J_SUCCESS
        self._msg = ""
        self._ret = {}
    
    @classmethod
    def success(cls, msg):
        j = cls()
        j._msg = msg
        
        return j
    
    @classmethod
    def redirect(cls, url):
        j = cls()
        j._code = cls.J_REDIRECT
        j._msg = url
        
        return j
    
    @classmethod
    def error(cls, code, msg):
        j = cls()
        j._code = code
        j._msg = msg
        
        return j
    
    def set_value(self, key, value):
        self._ret[key] = value
    
    def get_data(self):
        data = {}
        data['code'] = self._code
        data['msg'] = self._msg
        data['ret'] = self._ret
        
        return data
    
    def __str__(self):
        return "%d %s [%s]" % (self._code, self._msg, self._ret)

class AjaxResponseMixin(object):
    def ajax_response(self, json_data):
        return HttpResponse(json.dumps(json_data.get_data()), content_type="application/json")

class ForumIndexView(TemplateView):
    template_name = "forum/index.html"
    
    def get_context_data(self, **kwargs):
        data = super(ForumIndexView, self).get_context_data(**kwargs)
        
        page = self.request.GET.get('page')
        order = self.kwargs.get('filter', 'default')
        
        if order == 'star':
            topics = Topic.objects.filter(admin_star=True).all()
        elif order == 'latest':
            topics = Topic.objects.order_by('-rank', '-date_created').all()
        elif order == 'reply':
            topics = Topic.objects.order_by('-rank', '-last_replied').all()
        else:
            order = 'default'
            topics = Topic.objects.all()
        
        data['order'] = order
        topic_list, page_list = topic_pagination(page, topics)
        
        data['topics'] = topic_list
        data['page_list'] = page_list
        
        sections = Section.objects.filter(order__gt=0).all()
        s_list = []
        for s in sections:
            if s.nodes.all():
                tmp = {}
                tmp['name'] = s.name
                tmp['nodes'] = s.nodes.all()
                s_list.append(tmp)
        data['sections'] = s_list
        
        return data

forum_index = ForumIndexView.as_view()

class NodeView(TemplateView):
    template_name = "forum/node.html"
    
    def get_context_data(self, **kwargs):
        data = super(NodeView, self).get_context_data(**kwargs)
        
        node_id = self.kwargs['node_id']
        node = get_object_or_404(Node, id=node_id)
        page = self.request.GET.get('page')
        order = self.kwargs.get('filter', 'default')
        
        if order == 'star':
            topics = node.topics.filter(admin_star=True).all()
        elif order == 'latest':
            topics = node.topics.order_by('rank', '-date_created').all()
        elif order == 'reply':
            topics = node.topics.order_by('rank', '-last_replied').all()
        else:
            order = 'default'
            topics = node.topics.all()
        
        watch = False
        if self.request.user.is_authenticated():
            watch = self.request.user.watch_nodes.filter(id=node_id).exists()
        
        topic_list, page_list = topic_pagination(page, topics)
        data['node'] = node
        data['order'] = order
        data['topics'] = topic_list
        data['page_list'] = page_list
        data['watching'] = watch
        
        return data

node_view = NodeView.as_view()

@method_decorator(login_required, name='dispatch')
class CreateTopicView(TemplateView):
    template_name = "forum/create_topic.html"
    
    def get_context_data(self, **kwargs):
        data = super(CreateTopicView, self).get_context_data(**kwargs)
        
        node_id = self.kwargs.get('node_id', None)
        default_data = {'node': node_id}
        
        form = TopicForm(self.request.POST or None, initial=default_data)
        data["form"] = form
        data["authority"] = self.request.user.profile.can_create_topic()
        
        return data
    
    def post(self, request, *args, **kwargs):
        data = self.get_context_data()
        form = data["form"]
        
        if not self.request.user.profile.can_create_topic():
            return super(CreateTopicView, self).render_to_response(data)
        
        if form.is_valid():
            title = form.cleaned_data['title']
            md = form.cleaned_data['content']
            node = form.cleaned_data['node']
            rendered = render_markdown(md)
            abstract = Truncator(strip_tags(rendered)).chars(60)
            
            if node.is_trash:
                rank = 0
            else:
                rank = 10
            topic = Topic(node=node, author=request.user, title=title,
                          markdown=md, content=rendered, abstract=abstract, rank=rank)
            mentioned = get_metioned_user(request.user, md)
            
            self._commit_changes(topic, mentioned)
            
            return HttpResponseRedirect(reverse('topic_view', kwargs={'topic_id':topic.id}))
        
        return super(CreateTopicView, self).render_to_response(data)
    
    @transaction.atomic
    def _commit_changes(self, topic, mentioned_user):
        topic.save()
        
        if mentioned_user:
            for u in mentioned_user:
                data = {}
                data['topic'] = topic
                
                detail = render_to_string("forum/notification/create_topic_notification.html", data)
                n = Notification(user=u, detail=detail.strip())
                u.profile.has_notification = True
                u.profile.save()
                u.save()
                n.save()

create_topic_view = CreateTopicView.as_view()

@method_decorator(login_required, name='dispatch')
@method_decorator(author_required, name='dispatch')
class UpdateTopicView(TemplateView):
    template_name = "forum/update_topic.html"
    
    def get_context_data(self, **kwargs):
        data = super(UpdateTopicView, self).get_context_data(**kwargs)
        
        topic_id = self.kwargs.get('topic_id')
        topic = get_object_or_404(Topic, id=topic_id)
        default_data = {'title': topic.title,
                        'content': topic.markdown,
                        'node': topic.node}
        
        form = TopicForm(self.request.POST or None, initial=default_data)
        data["form"] = form
        data["topic_id"] = topic_id
        
        return data
    
    def post(self, request, *args, **kwargs):
        data = self.get_context_data()
        form = data["form"]
        if form.is_valid():
            title = form.cleaned_data['title']
            md = form.cleaned_data['content']
            node = form.cleaned_data['node']
            rendered = render_markdown(md)
            abstract = Truncator(strip_tags(rendered)).chars(60)
            
            topic_id = self.kwargs.get('topic_id')
            topic = get_object_or_404(Topic, id=topic_id)
            topic.node = node
            topic.title = title
            topic.markdown = md
            topic.content = rendered
            topic.abstract = abstract
            if node.is_trash:
                topic.rank = 0
            else:
                topic.rank = 10
            topic.save()
            
            return HttpResponseRedirect(reverse('topic_view', kwargs={'topic_id':topic_id}))
        
        return super(UpdateTopicView, self).render_to_response(data)

update_topic_view = UpdateTopicView.as_view()

class TopicView(TemplateView):
    template_name = "forum/topic.html"
    
    def get_context_data(self, **kwargs):
        data = super(TopicView, self).get_context_data(**kwargs)
        
        topic_id = self.kwargs['topic_id']
        topic = get_object_or_404(Topic, id=topic_id)
        data['topic'] = topic
        topic.viewed += 1
        topic.save()
        
        replies = topic.replies.all()
        
        paginator = Paginator(replies, 10)
        page = self.request.GET.get('page')
        try:
            reply_list = paginator.page(page)
        except PageNotAnInteger:
            reply_list = paginator.page(paginator.num_pages)
        except EmptyPage:
            reply_list = paginator.page(paginator.num_pages)
        
        page_list = get_pagination(reply_list.number, paginator.num_pages, 2)
        
        ilike = False
        if self.request.user.is_authenticated():
            ilike = self.request.user.like_topics.filter(id=topic_id).exists()
        
        data['replies'] = reply_list
        data['page_list'] = page_list
        data['form'] = ReplyForm()
        data['ilike'] = ilike
        
        return data

topic_view = TopicView.as_view()

@method_decorator(login_required, name='dispatch')
class ReplyTopicView(View):
    def post(self, request, *args, **kwargs):
        topic_id = self.kwargs['topic_id']
        topic = get_object_or_404(Topic, id=topic_id)
        form = ReplyForm(self.request.POST)
        if form.is_valid():
            md = form.cleaned_data['content']
            rendered = render_markdown(md)
            reply = Reply(topic=topic, author=request.user, markdown=md, content=rendered)
            
            mentioned = get_metioned_user(request.user, md)
            self._commit_changes(topic, reply, mentioned)
        
        return HttpResponseRedirect(reverse('topic_view', kwargs={'topic_id':topic_id}))
    
    @transaction.atomic
    def _commit_changes(self, topic, reply, mentioned_user):
        topic.reply_count += 1
        if not topic.reply_reward and topic.reply_count >= 10:
            user_reward(topic.author, settings.REP_TOPIC_REPLY, topic_id=topic.id)
            topic.reply_reward = True
            topic.author.profile.save()
        
        if mentioned_user:
            for u in mentioned_user:
                data = {}
                data['replier'] = reply.author
                data['topic'] = topic
                
                detail = render_to_string("forum/notification/reply_notification.html", data)
                n = Notification(user=u, detail=detail.strip())
                u.profile.has_notification = True
                u.profile.save()
                n.save()
        
        topic.last_replied = timezone.now()
        
        reply.save()
        topic.save()

reply_topic_view = ReplyTopicView.as_view()

@method_decorator(login_required, name='dispatch')
class WatchNodeView(AjaxResponseMixin, View):
    def post(self, request, *args, **kwargs):
        node_id = self.kwargs.get('node_id')
        watch = self.request.POST.get('watch')

        watching = False
        if watch == 'true':
            watching = True
        
        try:
            node = Node.objects.get(id=node_id)
            if watching:
                node.watcher.remove(request.user)
                watching = False
            else:
                node.watcher.add(request.user)
                watching = True
        except Node.DoesNotExist:
            json_data = JsonReturn.error(JsonReturn.J_ERROR,str(_("the node dose not exist")))
        except:
            json_data = JsonReturn.error(JsonReturn.J_ERROR, str(_("unknown error")))
        else:
            json_data = JsonReturn.success("ok")
            json_data.set_value('nodeid', node_id)
            json_data.set_value('watching', watching)
        
        return self.ajax_response(json_data)

watch_node_view = WatchNodeView.as_view()

@method_decorator(login_required, name='dispatch')
class LikeTopicView(AjaxResponseMixin, View):
    def post(self, request, *args, **kwargs):
        topic_id = self.kwargs.get('topic_id')
        like = self.request.POST.get('like')

        ilike = False
        if like == 'true':
            ilike = True
        
        try:
            topic = Topic.objects.get(id=topic_id)
            if ilike:
                topic.liker.remove(request.user)
                ilike = False
            else:
                topic.liker.add(request.user)
                ilike = True
                
                if not topic.like_reward and topic.liker.count() >= 10:
                    user_reward(topic.author, settings.REP_TOPIC_LIKE, topic_id=topic.id)
                    topic.like_reward = True
                    topic.author.profile.save()
            
        except Topic.DoesNotExist:
            json_data = JsonReturn.error(JsonReturn.J_ERROR,str(_("the topic dose not exist")))
        except:
            json_data = JsonReturn.error(JsonReturn.J_ERROR, str(_("unknown error")))
        else:
            json_data = JsonReturn.success("ok")
            json_data.set_value('topicid', topic_id)
            json_data.set_value('ilike', ilike)
#             json_data.set_value('count', topic.liker.count())
        
        return self.ajax_response(json_data)

like_topic_view = LikeTopicView.as_view()

class RenderMarkdownView(AjaxResponseMixin, View):
    def post(self, request, *args, **kwargs):
        md = self.request.POST.get('md')
        rendered = render_markdown(md)
        
        json_data = JsonReturn.success("ok")
        json_data.set_value('rendered', rendered)
        
        return self.ajax_response(json_data)

render_markdown_view = RenderMarkdownView.as_view()
