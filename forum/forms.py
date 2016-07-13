from django import forms
from django.utils.translation import ugettext_lazy as _
from forum.models import Node

class TopicForm(forms.Form):
    title = forms.CharField(label=_("Topic title"), max_length=120,
        widget=forms.TextInput(attrs={'placeholder': _('Topic title')}),
        error_messages={'required': _("title can't be blank"),
                        'max_length': _('The title should be no longer than 120 characters')})
    content = forms.CharField(widget=forms.Textarea(attrs={'rows':4, 'placeholder': _('Say something')}),
        error_messages={'required': _("content can't be blank")})
    node = forms.ModelChoiceField(queryset=Node.objects.all(), empty_label=_('---- select a node ----'),
        error_messages={'required': _("node can't be blank"), 'invalid_choice': _("invalid choice")})

class ReplyForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={'rows':4, 'placeholder': _('Leave a comment')}),
        error_messages={'required': _("content can't be blank")})
