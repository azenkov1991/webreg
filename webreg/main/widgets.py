from django.forms import MultiValueField, CharField, ChoiceField, MultiWidget, TextInput, Select


class PhoneWidget(MultiWidget):
    def __init__(self, attrs=None):
        widgets = [
            TextInput(attrs={'size': 3, 'maxlength': 3, 'placeholder': '999', 'class': 'phone-input-part'}),
            TextInput(attrs={'size': 3, 'maxlength': 3, 'placeholder': '999', 'class': 'phone-input-part'}),
            TextInput(attrs={'size': 2, 'maxlength': 2, 'placeholder': '99', 'class': 'phone-input-part'}),
            TextInput(attrs={'size': 2, 'maxlength': 2, 'placeholder': '99', 'class': 'phone-input-part'}),
        ]
        super(PhoneWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value[2:5], value[5:8], value[8:10], value[10:12]]
        else:
            return ['', '', '', '']

    def format_output(self, rendered_widgets):
        return '+7' + '(' + rendered_widgets[0] + ')-' + rendered_widgets[1] +\
               '-' + rendered_widgets[2] + '-' + rendered_widgets[3]


class PhoneField(MultiValueField):
    def __init__(self, *args, **kwargs):
        list_fields = [
            CharField(),
            CharField(),
            CharField(),
            CharField()
        ]
        super(PhoneField, self).__init__(list_fields, widget=PhoneWidget(), *args, **kwargs)

    def compress(self, values):
        return '+7' + values[0] + values[1] + values[2] + values[3]

