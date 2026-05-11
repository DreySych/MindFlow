import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .services import AiSearchService
from .strategies import AllQuestionsStrategy, LastNQuestionsStrategy

service = AiSearchService(strategy=LastNQuestionsStrategy(30))


def ai_search_page(request):
    """ Страница ИИ‑поиска, сразу рендерит ai.html """
    query = (request.GET.get("q") or "").strip()
    return render(request, "ai.html", {"query": query})


@csrf_exempt
@require_POST
def ai_search_api(request):
    """ API‑эндпоинт для ИИ‑поиска. Возвращает JSON {"answer": "..."} или {"error": "..."}. """
    try:
        data = json.loads(request.body.decode("utf-8"))
        query = (data.get("q") or "").strip()
    except Exception:
        return JsonResponse({"error": "Некорректный формат запроса"}, status=400)

    # Небольшой пример переключения стратегии:
    # если в query есть слово "все" — используем AllQuestionsStrategy; иначе LastNQuestionsStrategy.
    if "все" in query.lower():
        service.set_strategy(AllQuestionsStrategy())
    else:
        service.set_strategy(LastNQuestionsStrategy(30))

    result = service.search(query)

    if result.error:
        return JsonResponse({"error": result.error}, status=400)

    return JsonResponse({"answer": result.answer})
