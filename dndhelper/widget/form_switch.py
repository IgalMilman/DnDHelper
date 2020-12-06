from django import forms

class SwitchOnOffWidget(forms.CheckboxInput):
    template_name = 'forms/widget/switch.html'

    def __init__(self, attrs=None, check_test=None):
        super(SwitchOnOffWidget, self).__init__(attrs=attrs, check_test=check_test)
        self.label_text = ""

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['label_text']= self.label_text
        return context


class SwitchOnOffField(forms.BooleanField):
    widget = SwitchOnOffWidget
    
    def __init__(self, *args, **kwargs):
        super(SwitchOnOffField, self).__init__(*args, **kwargs)
        self.widget.label_text = self.label
        self.label = ""