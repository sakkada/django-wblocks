# -*- coding: utf-8 -*-
import itertools

from django import template
from django.conf import settings
from django.contrib.admin.utils import quote
from django.contrib.humanize.templatetags.humanize import intcomma
from django.contrib.messages.constants import DEFAULT_TAGS as MESSAGE_TAGS
from django.template.defaultfilters import stringfilter
from django.template.loader import render_to_string
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from wblocks.core.utils import cautious_slugify as _cautious_slugify
from wblocks.core.utils import camelcase_to_underscore, escape_script

register = template.Library()

register.filter('intcomma', intcomma)


@register.filter("ellipsistrim")
def ellipsistrim(value, max_length):
    if len(value) > max_length:
        truncd_val = value[:max_length]
        if not len(value) == (max_length + 1) and value[max_length + 1] != " ":
            truncd_val = truncd_val[:truncd_val.rfind(" ")]
        return truncd_val + "…"
    return value


@register.filter
def fieldtype(bound_field):
    try:
        return camelcase_to_underscore(bound_field.field.__class__.__name__)
    except AttributeError:
        try:
            return camelcase_to_underscore(bound_field.__class__.__name__)
        except AttributeError:
            return ""


@register.filter
def widgettype(bound_field):
    try:
        return camelcase_to_underscore(bound_field.field.widget.__class__.__name__)
    except AttributeError:
        try:
            return camelcase_to_underscore(bound_field.widget.__class__.__name__)
        except AttributeError:
            return ""


@register.simple_tag
def hook_output(hook_name):
    """
    Example: {% hook_output 'insert_editor_css' %}
    Whenever we have a hook whose functions take no parameters and return a string, this tag can be used
    to output the concatenation of all of those return values onto the page.
    Note that the output is not escaped - it is the hook function's responsibility to escape unsafe content.
    """
    snippets = [fn() for fn in hooks.get_hooks(hook_name)]
    return mark_safe(''.join(snippets))


@register.simple_tag
def usage_count_enabled():
    return getattr(settings, 'WAGTAIL_USAGE_COUNT_ENABLED', False)


@register.simple_tag
def base_url_setting():
    return getattr(settings, 'BASE_URL', None)


@register.simple_tag
def allow_unicode_slugs():
    return getattr(settings, 'WAGTAIL_ALLOW_UNICODE_SLUGS', True)


@register.simple_tag
def auto_update_preview():
    return getattr(settings, 'WAGTAIL_AUTO_UPDATE_PREVIEW', False)


class EscapeScriptNode(template.Node):
    TAG_NAME = 'escapescript'

    def __init__(self, nodelist):
        super().__init__()
        self.nodelist = nodelist

    def render(self, context):
        out = self.nodelist.render(context)
        return escape_script(out)

    @classmethod
    def handle(cls, parser, token):
        nodelist = parser.parse(('end' + EscapeScriptNode.TAG_NAME,))
        parser.delete_first_token()
        return cls(nodelist)


register.tag(EscapeScriptNode.TAG_NAME, EscapeScriptNode.handle)


# Helpers for Widget.render_with_errors, our extension to the Django widget API that allows widgets to
# take on the responsibility of rendering their own error messages
@register.filter
def render_with_errors(bound_field):
    """
    Usage: {{ field|render_with_errors }} as opposed to {{ field }}.
    If the field (a BoundField instance) has errors on it, and the associated widget implements
    a render_with_errors method, call that; otherwise, call the regular widget rendering mechanism.
    """
    widget = bound_field.field.widget
    if bound_field.errors and hasattr(widget, 'render_with_errors'):
        return widget.render_with_errors(
            bound_field.html_name,
            bound_field.value(),
            attrs={'id': bound_field.auto_id},
            errors=bound_field.errors
        )
    else:
        return bound_field.as_widget()


@register.filter
def has_unrendered_errors(bound_field):
    """
    Return true if this field has errors that were not accounted for by render_with_errors, because
    the widget does not support the render_with_errors method
    """
    return bound_field.errors and not hasattr(bound_field.field.widget, 'render_with_errors')


@register.filter(is_safe=True)
@stringfilter
def cautious_slugify(value):
    return _cautious_slugify(value)


@register.filter('abs')
def _abs(val):
    return abs(val)
