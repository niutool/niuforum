import re
import mistune
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

def block_code(text, lang, inlinestyles=False, linenos=False):
    if not lang:
        text = text.strip()
        return u'<pre><code>%s</code></pre>\n' % mistune.escape(text)

    try:
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = HtmlFormatter(
            noclasses=inlinestyles, linenos=linenos
        )
        code = highlight(text, lexer, formatter)
        if linenos:
            return '<div class="highlight-wrapper">%s</div>\n' % code
        return code
    except:
        return '<pre class="%s"><code>%s</code></pre>\n' % (
            lang, mistune.escape(text)
        )

class HighlightMixin(object):
    def block_code(self, text, lang):
        # renderer has an options
        inlinestyles = self.options.get('inlinestyles')
        linenos = self.options.get('linenos')
        return block_code(text, lang, inlinestyles, linenos)

class UserLinkRendererMixin(object):
    def user_link(self, user):
        try:
            u = User.objects.get(username=user)
        except User.DoesNotExist:
            u = None
        
        if u:
            uurl = reverse('user_profile', kwargs={'user_id':u.username})
            return "<a class='user niu-link' href='%s'>@%s</a>" % (uurl, user)
        else:
            return "@"+user

class NiuRenderer(HighlightMixin, UserLinkRendererMixin, mistune.Renderer):
    def __init__(self, *args, **kwargs):
        super(NiuRenderer, self).__init__(*args, **kwargs)
        self.user_link_rule = re.compile(r'@(\w+)', re.M)
    
    def text(self, text):
        new_text = ""
        while(True):
            m = self.user_link_rule.search(text)
            if not m:
                new_text += super(NiuRenderer, self).text(text)
                break
            
            new_text += super(NiuRenderer, self).text(text[:m.start()])
            new_text += self.user_link(m.group(1))
            text = text[m.end():]
        
        return new_text

renderer = NiuRenderer(linenos=False, inlinestyles=False)
mdp = mistune.Markdown(escape=True, renderer=renderer)

def render_markdown(md):
    rendered = mdp(md)
#     print(type(rendered), rendered)
    
    return rendered
