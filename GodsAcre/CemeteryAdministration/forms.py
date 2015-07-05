from django import forms


class YearsForm(forms.Form):
    years = forms.CharField(label='Ani', min_length=1, max_length=100)