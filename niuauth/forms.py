from django import forms
from django.utils.translation import ugettext_lazy as _

class ProfileForm(forms.Form):
    avatar = forms.ImageField(required=False, label=_("Select a new picture"),
                              help_text=_("The maximum image size you can upload is 2M"))
    display_name = forms.CharField(required=False, label=_("Name"), max_length=64)
    description = forms.CharField(widget=forms.Textarea(attrs={'rows':4,'placeholder': _('Tell a little about yourself')}),
                                  required=False, label=_("Bio"), max_length=256)
    website = forms.URLField(required=False, label=_('Website'))
    company = forms.CharField(required=False, label=_("Company"), max_length=64)
    email = forms.EmailField(required=False, label=_("E-mail address"))
    location = forms.CharField(required=False, label=_("Location"), max_length=128)
    github = forms.URLField(required=False, label=_('Github'))
    gitlab = forms.URLField(required=False, label=_('Gitlab'))
