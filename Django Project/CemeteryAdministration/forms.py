from django import forms


class YearsForm(forms.Form):
    ani = forms.CharField(label='Ani:', min_length=1, max_length=100,
                          widget=forms.TextInput(attrs={'placeholder': 'Unul sau mai multi ani',
                                                        'pattern': '^\s*\'?\s*\d+(\s*,?\s*\'?\s*\d+)*\s*$',
                                                        'title': 'Ani separati prin spatiu sau virgula (15 devine 2015, 94 devine 1994)',
                                                        'data-toggle': 'tooltip',
                                                        }))