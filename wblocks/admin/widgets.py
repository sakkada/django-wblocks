import itertools
import json
from functools import total_ordering

from django.conf import settings
from django.forms import widgets
from django.forms.utils import flatatt
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.formats import get_format
from django.utils.functional import cached_property
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from wblocks.admin.datetimepicker import to_datetimepicker_format
from wblocks.utils.widgets import WidgetWithScript

DEFAULT_DATE_FORMAT = '%Y-%m-%d'
DEFAULT_DATETIME_FORMAT = '%Y-%m-%d %H:%M'


class AdminAutoHeightTextInput(WidgetWithScript, widgets.Textarea):
    def __init__(self, attrs=None):
        # Use more appropriate rows default, given autoheight will alter this anyway
        default_attrs = {'rows': '1'}
        if attrs:
            default_attrs.update(attrs)

        super(AdminAutoHeightTextInput, self).__init__(default_attrs)

    def render_js_init(self, id_, name, value):
        return 'autosize($("#{0}"));'.format(id_)


class AdminDateInput(WidgetWithScript, widgets.DateInput):
    def __init__(self, attrs=None, format=None):
        fmt = format
        if fmt is None:
            fmt = getattr(settings, 'WAGTAIL_DATE_FORMAT', DEFAULT_DATE_FORMAT)
        self.js_format = to_datetimepicker_format(fmt)
        super(AdminDateInput, self).__init__(attrs=attrs, format=fmt)

    def render_js_init(self, id_, name, value):
        config = {
            'dayOfWeekStart': get_format('FIRST_DAY_OF_WEEK'),
            'format': self.js_format,
        }
        return 'initDateChooser({0}, {1});'.format(
            json.dumps(id_),
            json.dumps(config)
        )


class AdminTimeInput(WidgetWithScript, widgets.TimeInput):
    def __init__(self, attrs=None, format='%H:%M'):
        super(AdminTimeInput, self).__init__(attrs=attrs, format=format)

    def render_js_init(self, id_, name, value):
        return 'initTimeChooser({0});'.format(json.dumps(id_))


class AdminDateTimeInput(WidgetWithScript, widgets.DateTimeInput):
    def __init__(self, attrs=None, format=None):
        fmt = format
        if fmt is None:
            fmt = getattr(settings, 'WAGTAIL_DATETIME_FORMAT', DEFAULT_DATETIME_FORMAT)
        self.js_format = to_datetimepicker_format(fmt)
        super(AdminDateTimeInput, self).__init__(attrs=attrs, format=fmt)

    def render_js_init(self, id_, name, value):
        config = {
            'dayOfWeekStart': get_format('FIRST_DAY_OF_WEEK'),
            'format': self.js_format,
        }
        return 'initDateTimeChooser({0}, {1});'.format(
            json.dumps(id_),
            json.dumps(config)
        )


class AdminChooser(WidgetWithScript, widgets.Input):
    input_type = 'hidden'
    choose_one_text = _("Choose an item")
    choose_another_text = _("Choose another item")
    clear_choice_text = _("Clear choice")
    link_to_chosen_text = _("Edit this item")
    show_edit_link = True

    # when looping over form fields, this one should appear in visible_fields, not hidden_fields
    # despite the underlying input being type="hidden"
    is_hidden = False

    def get_instance(self, model_class, value):
        # helper method for cleanly turning 'value' into an instance object
        if value is None:
            return None

        try:
            return model_class.objects.get(pk=value)
        except model_class.DoesNotExist:
            return None

    def get_instance_and_id(self, model_class, value):
        if value is None:
            return (None, None)
        elif isinstance(value, model_class):
            return (value, value.pk)
        else:
            try:
                return (model_class.objects.get(pk=value), value)
            except model_class.DoesNotExist:
                return (None, None)

    def value_from_datadict(self, data, files, name):
        # treat the empty string as None
        result = super(AdminChooser, self).value_from_datadict(data, files, name)
        if result == '':
            return None
        else:
            return result

    def __init__(self, **kwargs):
        # allow choose_one_text / choose_another_text to be overridden per-instance
        if 'choose_one_text' in kwargs:
            self.choose_one_text = kwargs.pop('choose_one_text')
        if 'choose_another_text' in kwargs:
            self.choose_another_text = kwargs.pop('choose_another_text')
        if 'clear_choice_text' in kwargs:
            self.clear_choice_text = kwargs.pop('clear_choice_text')
        if 'link_to_chosen_text' in kwargs:
            self.link_to_chosen_text = kwargs.pop('link_to_chosen_text')
        if 'show_edit_link' in kwargs:
            self.show_edit_link = kwargs.pop('show_edit_link')
        super(AdminChooser, self).__init__(**kwargs)
