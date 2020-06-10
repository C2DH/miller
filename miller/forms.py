from django import forms


class CaptionForm(forms.Form):
    document = forms.RegexField(max_length=150, regex=r'^[a-zA-Z\-\_\.\d]+$', required=True)
    story = forms.RegexField(max_length=150, regex=r'^[a-zA-Z\-\_\.\d]+$', required=True)


class ExtractCaptionFromStory(forms.Form):
    key = forms.ChoiceField(choices=[('slug', 'slug'), ('pk', 'pk'), ('id', 'id')], required=True)
    parser = forms.ChoiceField(choices=[('json', 'json')], required=True)
