from django import forms


class QuestionForm(forms.Form):
	variants = (
		(0, "Выберите тему"),
		(1, 'Программирование на Python'),
		(2, 'Визуальное программирование на Python'),
		(3, 'UI/UX'),
		(4, 'Форматы данных'),
		(5, 'Программирование на С++'),
		(6, 'Программирование на С#'),
		(7, 'Дискретная математика'),
		(8, 'Компьютерные сети'),
		(9, 'Промышленное программирование')
				)
	title = forms.CharField()
	description = forms.CharField()
	theme = forms.ChoiceField(choices=variants)
	tags = forms.CharField(required=False)
	images = forms.CharField(required=False)