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
    title = forms.CharField()
    description = forms.CharField(required=False)
    # tags = forms.CharField(required=False)
    images = MultipleFileField(required=False, label='Изображения')


class CommentForm(forms.Form):
    text = forms.CharField(label='Комментарий')


class AnswerForm(forms.Form):
    text = forms.CharField()
