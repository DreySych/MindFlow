from django import forms


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class QuestionForm(forms.Form):
    file = open('questions/available_tags.txt', mode='r', encoding='utf-8')
    available_tags = file.read().split('\n')
    file.close()

    CHOICES = [(i, i) for i in available_tags]

    title = forms.CharField()
    description = forms.CharField(required=False)
    images = MultipleFileField(required=False, label='Изображения')
    tag = forms.ChoiceField(choices=CHOICES)


class CommentForm(forms.Form):
    text = forms.CharField(label='Комментарий')


class AnswerForm(forms.Form):
    text = forms.CharField()
