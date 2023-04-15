from django.contrib.admin.widgets import AdminFileWidget
from django.utils.html import format_html


class CustomAdminFileWidget(AdminFileWidget):
    template_name = 'custom_clearable_file_input.html'
    # def render(self, name, value, attrs=None, renderer=None):
    #     return format_html(super().render(name, value, attrs, renderer))
