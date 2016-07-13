import re
from PIL import Image, ImageOps
from io import BytesIO
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.core.files.uploadedfile import SimpleUploadedFile
from forum.models import Topic

MENTION_REGEX = re.compile(r'@(\w+)', re.M)
IMAGE_LARGE = 144
IMAGE_MEDIUM = 96
IMAGE_SMALL = 48
NUM_PER_PAGE = 20

def _thumbnail(upload, size, fmt):
    img = ImageOps.fit(upload, size, Image.ANTIALIAS)
    
    temp = BytesIO()
    img.save(temp, fmt, quality=95)
    temp.seek(0)
    
    return temp

def create_thumbnail(src, new_name, ext):
    upload = Image.open(BytesIO(src.read()))
    fmt = src.content_type.split('/')[-1]
    
    large = _thumbnail(upload, (IMAGE_LARGE, IMAGE_LARGE), fmt)
    filename_l = "%s_l.%s" % (new_name, ext)
    large_file = SimpleUploadedFile(filename_l, large.read(), content_type=src.content_type)
    
    medium = _thumbnail(upload, (IMAGE_MEDIUM, IMAGE_MEDIUM), fmt)
    filename_m = "%s_m.%s" % (new_name, ext)
    medium_file = SimpleUploadedFile(filename_m, medium.read(), content_type=src.content_type)
    
    small = _thumbnail(upload, (IMAGE_SMALL, IMAGE_SMALL), fmt)
    filename_s = "%s_s.%s" % (new_name, ext)
    small_file = SimpleUploadedFile(filename_s, small.read(), content_type=src.content_type)
    
    return large_file, medium_file, small_file

def get_pagination(current_page, num_pages, count):
    page_list = []
    
    show_pages = 2*count+1
    if show_pages >= num_pages:
        page_list.extend(range(1, num_pages+1))
    elif current_page - count < 1:
        page_list.extend(range(1, show_pages+1))
    elif current_page + count > num_pages:
        page_list.extend(range(num_pages+1-show_pages, num_pages+1))
    else:
        page_list.extend(range(current_page-count, current_page+count+1))
    
    return page_list

def topic_pagination(page, topics):
    paginator = Paginator(topics, NUM_PER_PAGE)
    try:
        topic_list = paginator.page(page)
    except PageNotAnInteger:
        topic_list = paginator.page(1)
    except EmptyPage:
        topic_list = paginator.page(paginator.num_pages)
    
    page_list = get_pagination(topic_list.number, paginator.num_pages, 2)
    
    return topic_list, page_list

def author_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        topic_id = kwargs.get('topic_id')
        topic = get_object_or_404(Topic, id=topic_id)
        
        if topic.author == request.user:
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()
    
    return _wrapped_view_func

def get_metioned_user(sender, markdown):
    mentioned = set(re.findall(MENTION_REGEX, markdown)) - set([sender.username])
#     mentioned = set(re.findall(MENTION_REGEX, markdown))
    if mentioned:
        return User.objects.filter(username__in=mentioned)
    
    return None
