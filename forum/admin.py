from django.contrib import admin
from forum.models import Section, Node
from django.utils.crypto import get_random_string
from forum.utils import create_thumbnail

class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'last_modified')

class NodeAdmin(admin.ModelAdmin):
    exclude = ['icon_l', 'icon_m', 'icon_s']
    list_display = ('section', 'name', 'admin_image', 'description', 'order', 'last_modified')
    
    def save_model(self, request, obj, form, change):
        icon = form.cleaned_data['icon_raw']
        if icon:
            self._save_icon(obj, icon)
        
        super(NodeAdmin, self).save_model(request, obj, form, change)
    
    def _save_icon(self, obj, image):
        new_name = get_random_string(length=6)
        ext = image.name.split('.')[-1]
        image.name = '%s.%s' % (new_name, ext)
        
        large, medium, small = create_thumbnail(image, new_name, ext)
        obj.icon_raw = image
        obj.icon_l = large
        obj.icon_m = medium
        obj.icon_s = small

admin.site.register(Section, SectionAdmin)
admin.site.register(Node, NodeAdmin)
