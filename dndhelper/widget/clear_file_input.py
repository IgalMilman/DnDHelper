import os
from django import forms

class ClearFileInput(forms.ClearableFileInput):
    template_name = 'forms/widget/clear_file_input.html'

    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        if 'value' in context['widget'] and context['widget']['value']:
            context['widget']['value_file_name'] = os.path.basename(context['widget']['value'].name) + self.add_to_filename
        return context
