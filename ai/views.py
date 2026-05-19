import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string

from .services import AiSearchService
from .strategies import AllQuestionsStrategy, LastNQuestionsStrategy
from questions.models import Question, Like

service = AiSearchService(strategy=LastNQuestionsStrategy(30))


def ai_search_page(request):
    query = (request.GET.get("q") or "").strip()
    return render(request, "ai.html", {"query": query})


@csrf_exempt
@require_POST
def ai_search_api(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        query = (data.get("q") or "").strip()
        if len(query) > 500:
            return JsonResponse({"error": "Слишком длинный запрос"}, status=400)
    except Exception as e:
        print("ai_search_api JSON error:", repr(e))
        return JsonResponse({"error": "Некорректный формат запроса"}, status=400)

    try:
        if "все" in query.lower():
            service.set_strategy(AllQuestionsStrategy())
        else:
            service.set_strategy(LastNQuestionsStrategy(30))

        result = service.search(query)

        if result.error and not result.answer:
            return JsonResponse({"error": result.error}, status=400)

        question_ids = result.question_ids or []
        questions_qs = Question.objects.filter(id__in=question_ids)
        q_map = {q.id: q for q in questions_qs}
        ordered_questions = [q_map[qid] for qid in question_ids if qid in q_map]

        posts_context = []
        for question in ordered_questions:
            comments = question.comment_set.all()

            if request.user.is_authenticated:
                like_obj = Like.objects.filter(user=request.user, question=question).first()
                user_rating = like_obj.rating if like_obj else 0
            else:
                user_rating = 0

            posts_context.append({
                "question": question,
                "question_images": question.image_list,
                "comments": comments,
                "user_rating": user_rating,
            })

        html = render_to_string(
            "question_list_fragment.html",
            {"posts_context": posts_context},
            request=request,
        )

        return JsonResponse({
            "answer": result.answer or result.error or "",
            "html": html,
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": f"Внутренняя ошибка API: {e}"}, status=500)