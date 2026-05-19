from django.shortcuts import render, redirect
from django.http import JsonResponse
from complaints.models import Complaint
from users.models import User, Subscription
from notifications.models import Notification
from questions.models import Question, Comment, Answer
import logging

logger = logging.getLogger('project')


def accept(request):
    """Принимает жалобу и удаляет объект (вопрос/пользователя/комментарий/ответ)."""
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Только POST'}, status=405)
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/')

    complaint = Complaint.objects.filter(
        id=request.GET.get('complaint_id')).first()
    if complaint:
        if complaint.question:
            complaint.question.delete()
        elif complaint.user:
            complaint.user.active = False
            complaint.user.save()
        elif complaint.comment:
            complaint.comment.delete()
        elif complaint.answer:
            complaint.answer.delete()
        complaint.delete()

    return redirect(request.GET.get('to', '/'))


def decline(request):
    """Отклоняет жалобу (удаляет её без наказания)."""
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Только POST'}, status=405)
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/')

    complaint = Complaint.objects.filter(
        id=request.GET.get('complaint_id')).first()
    if complaint:
        complaint.delete()
    return redirect(request.GET.get('to', '/'))


def complaint_page(request):
    """Создаёт новую жалобу (POST) с проверками прав и дубликатов."""
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'ok': False, 'error': 'Требуется авторизация'})

        if not request.user.active:
            return JsonResponse({'ok': False, 'error': 'Вы заблокированы и не можете отправлять жалобы'})

        complaint_text = request.POST.get('description', '').strip()

        if not complaint_text:
            return JsonResponse({'ok': False, 'error': 'Введите текст жалобы'})

        if len(complaint_text) > 500:
            return JsonResponse({'ok': False, 'error': 'Максимум 500 символов'})

        question_id = request.GET.get('question_id')
        user_id = request.GET.get('user_id')
        comment_id = request.GET.get('comment_id')
        answer_id = request.GET.get('answer_id')
        if question_id:
            question = Question.objects.filter(id=question_id).first()

            if question and question.author == request.user:
                return JsonResponse({
                    'ok': False,
                    'error': 'Нельзя жаловаться на свой пост'
                })

        if user_id and str(user_id) == str(request.user.id):
            return JsonResponse({
                'ok': False,
                'error': 'Нельзя жаловаться на себя'
            })

        if comment_id:
            comment = Comment.objects.filter(id=comment_id).first()

            if comment and comment.author == request.user:
                return JsonResponse({
                    'ok': False,
                    'error': 'Нельзя жаловаться на свой комментарий'
                })
        if answer_id:
            answer = Answer.objects.filter(id=answer_id).first()

            if answer and answer.author == request.user:
                return JsonResponse({
                    'ok': False,
                    'error': 'Нельзя жаловаться на свой ответ'
                })
        if not question_id and not user_id and not comment_id and not answer_id:
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
            if answer_id:
                complaint.answer = Answer.objects.get(id=answer_id)

            exists = Complaint.objects.filter(
                author=request.user,
                question=complaint.question if question_id else None,
                user=complaint.user if user_id else None,
                comment=complaint.comment if comment_id else None,
                answer=complaint.answer if answer_id else None,
            ).exists()

            if exists:
                return JsonResponse({
                    'ok': False,
                    'error': 'Жалоба уже отправлена'
                })

            complaint.save()
            logger.info('Complaint created by user=%s', request.user.username)

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
        except Answer.DoesNotExist:
            return JsonResponse({'ok': False, 'error': 'Ответ не найден'})
        except Exception as e:
            logger.error('Complaint error: %s', e)
            return JsonResponse({'ok': False, 'error': 'Ошибка сервера'})

    return redirect('/')


def complaint_user_panel_page(request):
    """Панель модератора: все жалобы на пользователей."""
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
    """Панель модератора: все жалобы на вопросы."""
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/')

    complaints = Complaint.objects.filter(
        question__isnull=False).order_by('-id')
    context = {
        'complaints': complaints,
        'user': request.user,
        'subscriptions': Subscription.objects.filter(user1=request.user),
    }
    return render(request, "complains_panel_post.html", context)


def complaint_comment_panel_page(request):
    """Панель модератора: жалобы на комментарии и ответы (с обрезкой пробелов)."""
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/')

    complaints = Complaint.objects.filter(
        comment__isnull=False
    ).order_by('-id') | Complaint.objects.filter(
        answer__isnull=False
    ).order_by('-id')

    for complaint in complaints:
        if complaint.comment and complaint.comment.text:
            complaint.comment.text = complaint.comment.text.lstrip()
        elif complaint.answer and complaint.answer.answer:
            complaint.answer.answer = complaint.answer.answer.lstrip()

    context = {
        'complaints': complaints,
        'user': request.user,
        'subscriptions': Subscription.objects.filter(user1=request.user),
    }
    return render(request, "complains_panel_comment.html", context)