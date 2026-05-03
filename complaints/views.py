from complaints.forms import *
from complaints.models import *
from django.shortcuts import render, redirect

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


def complaint_user_panel_page(request):
	if not request.user.is_staff:
		return redirect('/')
	context = {}

	complaints = Complaint.objects.filter(user__isnull=False)

	context['complaints'] = complaints

	return render(request, "complaint_user_panel.html", context)

def complaint_question_panel_page(request):
	if not request.user.is_staff:
		return redirect('/')
	context = {}

	complaints = Complaint.objects.filter(question__isnull=False)

	context['complaints'] = complaints

	return render(request, "complaint_question_panel.html", context)