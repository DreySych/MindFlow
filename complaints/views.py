from django.shortcuts import render, redirect
from django.http import JsonResponse
from complaints.models import Complaint
from questions.models import Question, Comment
from users.models import User, Subscription
from notifications.models import Notification


def accept(request):
    complaint = Complaint.objects.filter(id=request.GET.get('complaint_id')).first()
    if complaint:
        if complaint.question:
            complaint.question.delete()
        elif complaint.user:
            complaint.user.active = False
            complaint.user.save()
        elif complaint.comment:
            complaint.comment.delete()
        complaint.delete()
    return redirect(request.GET.get('to', '/'))


def decline(request):
    complaint = Complaint.objects.filter(id=request.GET.get('complaint_id')).first()
    if complaint:
        complaint.delete()
    return redirect(request.GET.get('to', '/'))


def complaint_page(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'ok': False, 'error': 'Требуется авторизация'})

        complaint_text = request.POST.get('description', '').strip()

        if not complaint_text:
            return JsonResponse({'ok': False, 'error': 'Введите текст жалобы'})

        if len(complaint_text) > 500:
            return JsonResponse({'ok': False, 'error': 'Максимум 500 символов'})

        question_id = request.GET.get('question_id')
        user_id = request.GET.get('user_id')
        comment_id = request.GET.get('comment_id')

        if not question_id and not user_id and not comment_id:
            return JsonResponse({'ok': False, 'error': 'Не указан объект жалобы'})

        try:
            complaint = Complaint()
            complaint.author = request.user
            complaint.description = complaint_text

            if question_id:
                complaint.question = Question.objects.get(id=question_id)
            if user_id:
                complaint.user = User.objects.get(id=user_id)
            if comment_id:
                complaint.comment = Comment.objects.get(id=comment_id)

            complaint.save()

            admins = User.objects.filter(is_staff=True)
            for admin in admins:
                Notification.objects.create(
                    user=admin,
                    text=f'{request.user.username} отправил жалобу',
                    link='/complaint/panel/questions/'
                )

            return JsonResponse({'ok': True})

        except Question.DoesNotExist:
            return JsonResponse({'ok': False, 'error': 'Пост не найден'})
        except User.DoesNotExist:
            return JsonResponse({'ok': False, 'error': 'Пользователь не найден'})
        except Comment.DoesNotExist:
            return JsonResponse({'ok': False, 'error': 'Комментарий не найден'})
        except Exception as e:
            print('Complaint error:', str(e))
            return JsonResponse({'ok': False, 'error': 'Ошибка сервера'})

    return redirect('/')


def complaint_user_panel_page(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/')

    complaints = Complaint.objects.filter(user__isnull=False).order_by('-id')
    context = {
        'complaints': complaints,
        'user': request.user,
        'subscriptions': Subscription.objects.filter(user1=request.user),
    }
    return render(request, "complains_panel_user.html", context)


def complaint_question_panel_page(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/')

    complaints = Complaint.objects.filter(question__isnull=False).order_by('-id')
    context = {
        'complaints': complaints,
        'user': request.user,
        'subscriptions': Subscription.objects.filter(user1=request.user),
    }
    return render(request, "complains_panel_post.html", context)


def complaint_comment_panel_page(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/')

    complaints = Complaint.objects.filter(comment__isnull=False).order_by('-id')
    context = {
        'complaints': complaints,
        'user': request.user,
        'subscriptions': Subscription.objects.filter(user1=request.user),
    }
    return render(request, "complains_panel_comment.html", context)