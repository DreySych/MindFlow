from complaints.forms import *
from complaints.models import *
from django.shortcuts import render

def complaint_page(request):
    context = {}

    question_id = request.GET.get('question_id')
    user_id = request.GET.get('user_id')

    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        complaint_text = form.data['description']

        if user_id and int(user_id) != int(request.user.id) or question_id:
            complaint = Complaint(author=request.user, description=complaint_text,
                                  question=Question.objects.filter(id=question_id)[
                                      0] if "question_id" in request.GET else None,
                                  user=User.objects.filter(id=user_id)[0] if "user_id" in request.GET else None)
            complaint.save()
    else:
        form = ComplaintForm()

    context['form'] = form

    return render(request, "complaint.html", context)