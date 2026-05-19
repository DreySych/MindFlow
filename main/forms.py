from django import forms


class SearchForm(forms.Form):
    input_text = forms.CharField()


class TagFilterForm(forms.Form):
    file = open('questions/available_tags.txt', mode='r', encoding='utf-8')
    available_tags = file.read().split('\n')
    file.close()

    CHOICES = [(i, i) for i in available_tags]

    tag = forms.ChoiceField(choices=CHOICES)
