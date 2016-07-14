from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from forum.models import Section, Node, Topic

ForumSection = {"name": "社区",
                "order": 1,
                "nodes": [("公告", False), ("反馈", False), ("回收站", True)]
                }

class Command(BaseCommand):
    help = 'initialize niuforum'

    def add_arguments(self, parser):
        parser.add_argument('user')

    def handle(self, *args, **options):
        username = options['user']
        user = User.objects.get(username=username)
        
        manager, _created = Group.objects.get_or_create(name="manager")
        manager.save()
        user.groups.add(manager)
        
        tmpnode = self._add_section(ForumSection)
        if tmpnode:
            about = Topic(node=tmpnode, author=user, title="about")
            about.save()
            privacy = Topic(node=tmpnode, author=user, title="privacy")
            privacy.save()
            credit = Topic(node=tmpnode, author=user, title="credit")
            credit.save()
            t = Topic(node=tmpnode, author=user, title="topic")
            t.save()
    
    def _add_section(self, section):
        name = section["name"]
        order = section["order"]
        nodes = section.get("nodes")
        
        s = Section(name=name, order=order)
        s.save()
        
        tmpnode = None
        if nodes:
            for n in nodes:
                name = n[0]
                is_trash = n[1]
                tmpnode = Node(section=s, name=name, is_trash=is_trash, description=name, order=1)
                tmpnode.save()
        
        return tmpnode
