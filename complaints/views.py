from complaints.forms import *
from complaints.models import *
from django.shortcuts import render, redirect, get_object_or_404

def accept(request):
	complaint = Complaint.objects.filter(id=request.GET.get('complaint_id'))[0]
	if complaint.question:
		complaint.question.delete()
	elif complaint.user:
		complaint.user.active = False
		complaint.user.save()
	elif complaint.comment:
		complaint.comment.delete()

	complaint.delete()

	return redirect(request.GET.get('to'))

def decline(request):
	complaint = Complaint.objects.filter(id=request.GET.get('complaint_id'))[0]
	complaint.delete()

	return redirect(request.GET.get('to'))

def complaint_page(request):
	if not request.user.active:
		return redirect('/')
	context = {}

	question_id = request.GET.get('question_id')
	user_id = request.GET.get('user_id')
	comment_id = request.GET.get('comment_id')

	if request.method == 'POST':
		form = ComplaintForm(request.POST)
		complaint_text = form.data['description']
		if not complaint_text.strip():
			return redirect(request.META.get('HTTP_REFERER', '/'))
		if user_id and int(user_id) != int(request.user.id) or question_id or comment_id:
			complaint = Complaint(author=request.user, description=complaint_text,
								  question=Question.objects.filter(id=question_id)[0] if "question_id" in request.GET else None,
								  user=User.objects.filter(id=user_id)[0] if "user_id" in request.GET else None,
								  comment=Comment.objects.filter(id=comment_id)[0] if "comment_id" in request.GET else None,
			)
			complaint.save()
	else:
		form = ComplaintForm()

	context['form'] = form
	context['subscriptions'] = Subscription.objects.filter(user1=request.user)

	return render(request, "complaint.html", context)


def complaint_user_panel_page(request):
	if not request.user.is_staff:
		return redirect('/')
	context = {}

	complaints = Complaint.objects.filter(user__isnull=False)

	context['complaints'] = complaints
	context['user'] = request.user
	context['subscriptions'] = Subscription.objects.filter(user1=request.user)

	return render(request, "complaint_user_panel.html", context)

def complaint_question_panel_page(request):
	if not request.user.is_staff:
		return redirect('/')
	context = {}

	complaints = Complaint.objects.filter(question__isnull=False)

	context['complaints'] = complaints
	context['user'] = request.user
	context['subscriptions'] = Subscription.objects.filter(user1=request.user)
	return render(request, "complaint_question_panel.html", context)

def complaint_comment_panel_page(request):
	if not request.user.is_staff:
		return redirect('/')
	context = {}

	complaints = Complaint.objects.filter(comment__isnull=False)

	context['complaints'] = complaints
	context['user'] = request.user
	context['subscriptions'] = Subscription.objects.filter(user1=request.user)

	return render(request, "complaint_comment_panel.html", context)