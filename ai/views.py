import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string

from .services import AiSearchService
from .strategies import AllQuestionsStrategy, LastNQuestionsStrategy
from main.views import perform_search, build_post_context

service = AiSearchService(strategy=LastNQuestionsStrategy(30))


def ai_search_page(request):
    query = (request.GET.get("q") or "").strip()
    return render(request, "ai.html", {"query": query})


@require_POST
def ai_search_api(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        query = (data.get("q") or "").strip()
        if len(query) > 500:
            return JsonResponse({"error": "Слишком длинный запрос"}, status=400)
    except Exception:
        return JsonResponse({"error": "Некорректный формат запроса"}, status=400)

    try:
        if "все" in query.lower():
            service.set_strategy(AllQuestionsStrategy())
        else:
            service.set_strategy(LastNQuestionsStrategy(30))

        result = service.search(query)

        if result.error and not result.answer:
            return JsonResponse({"error": result.error}, status=400)

        answer_text = result.answer or result.error or ""

        similar_questions = perform_search(query)
        similar_questions = similar_questions[:5]

        posts_context = [build_post_context(q, request) for q in similar_questions]

        html = ""
        for post_data in posts_context:
            html += render_to_string(
                "question_card.html",
                {
                    "question": post_data["question"],
                    "question_images": post_data["question_images"],
                    "comments": post_data["comments"],
                    "user_rating": post_data["user_rating"],
                    "request": request,
                    "user": request.user,
                },
            )

        return JsonResponse({
            "answer": answer_text,
            "html": html,
        })

    except Exception as e:
        return JsonResponse({"error": f"Внутренняя ошибка API: {e}"}, status=500)
