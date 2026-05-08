from django.shortcuts import render

# Create your views here.
def complain_question_page(request):
    return render(request, template_name="complain_question.html")

def complain_user_page(request):
    return render(request, template_name="complain_user.html")

def complain_comment_page(request):
    return render(request, template_name="complain_comment.html")


def complains_panel_page_c(request):
    return render(request, template_name="complains_panel_comment.html")

def complains_panel_page_p(request):
    return render(request, template_name="complains_panel_post.html")

def complains_panel_page_u(request):
    return render(request, template_name="complains_panel_user.html")