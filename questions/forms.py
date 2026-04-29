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
    # variants = (
    # 	(0, "Без темы"),
    # 	(1, 'Программирование на Python'),
    # 	(2, 'Визуальное программирование на Python'),
    # 	(3, 'UI/UX'),
    # 	(4, 'Форматы данных'),
    # 	(5, 'Программирование на С++'),
    # 	(6, 'Программирование на С#'),
    # 	(7, 'Дискретная математика'),
    # 	(8, 'Компьютерные сети'),
    # 	(9, 'Промышленное программирование')
    # 			)


    title = forms.CharField()
    description = forms.CharField()
    #theme = forms.ChoiceField(choices=variants)
    tags = forms.CharField(required=False)
    images = MultipleFileField(required=False, label='Изображения')

class ComplaintForm(forms.Form):
    description = forms.CharField()