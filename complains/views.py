from django.shortcuts import render

# Create your views here.
def complain_question_page(request):
    return render(request, template_name="complain_question.html")

def complain_user_page(request):
    return render(request, template_name="complain_user.html")

def complains_panel_page(request):
    return render(request, template_name="complains_panel.html")