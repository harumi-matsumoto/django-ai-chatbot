from django import forms

class TestPredictForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea, max_length=255)