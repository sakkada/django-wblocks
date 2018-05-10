import json

from django.conf import settings
from django.forms import widgets
from django.utils.formats import get_format
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
