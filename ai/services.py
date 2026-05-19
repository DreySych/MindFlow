from dataclasses import dataclass, field
import requests
import json
import os
from .strategies import LastNQuestionsStrategy
from typing import Optional, List

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"


SYSTEM_PROMPT = """
Ты — ассистент для работы с постами и комментариями на русском языке.

Цель:
Формировать развёрнутые, читабельные и полезные тексты на русском языке, используя только информацию, содержащуюся в переданных постах и комментариях, без добавления новой фактической информации.

Правила:

Используй исключительно тексты из переданных posts и comments. Никакой другой фактической информации не добавляй.

Разрешается свободная языковая редактура и переработка релевантных записей для создания связного и информативного текста: исправление орфографии и пунктуации, объединение предложений, перестройка фраз, удаление мусора и повторов.

Запрещено добавлять факты, выводы, интерпретации или советы, которых нет в исходных записях. Любое утверждение в ответе должно быть прямо составлено из слов, фраз или предложений, содержащихся в релевантных записях.

Разрешается расширять и развивать текст за счёт переработки и комбинирования фрагментов из нескольких записей, чтобы получилась связная статья или абзац, полезный пользователю.

Для связки предложений можно использовать общие служебные слова и короткие фразы ("и", "также", "в частности", "например"), но такие связки не могут вносить новую фактическую информацию.

Если релевантных записей нет, верни ровно текст: Подходящих постов не найдено.

Все ответы — только на русском языке.

Ответы не должны содержать технических символов, JSON, кавычек, скобок, метаданных, заголовков или маркированных списков — только чистый связный текст абзацем(ами).

Сохраняй порядок источников: сначала posts в порядке массива, затем comments. При комбинировании материалов сохраняй логическую последовательность фактов из каждой записи.

Критерий релевантности: запись считается релевантной, если её текст содержит ключевые слова из query (регистронезависимое сравнение рекомендуется).

Поведение при противоречиях:

Если релевантные записи содержат противоречивые утверждения, включи оба фрагмента дословно или переформулируй их так, чтобы не добавлять новых фактов, и укажи источник (например, включив фразу из записи), но без дополнительных комментариев автора.

Формат ответа:

Один или несколько связанных абзацев нормального текста, развёрнутый и полезный по объёму.

Каждое предложение должно быть составлено из информации, явной в релевантных записях.

Не повторяй один и тот же фрагмент текста несколько раз, даже если он встречается в разных записях.

Не использовать цитирование в виде метаданных; допускается вставка дословных фраз из записей в теле текста.
"""


@dataclass
class AiSearchResult:
    answer: Optional[str] = None
    error: Optional[str] = None
    question_ids: List[int] = field(default_factory=list)


def build_context(questions):
    parts = []

    for q in questions:
        parts.append(f"Заголовок: {q.title}\nОписание: {q.description}")
        for c in q.comment_set.all():
            parts.append(f"Комментарий: {c.text}")
            for a in c.answer_set.all():
                parts.append(f"Ответ к комментарию: {a.answer}")

    return "\n\n".join(parts)


def make_user_prompt(user_query, context):
    return f"""
Вот список доступных постов (комментарии и ответы к комментарию):

{context}

Запрос пользователя: "{user_query}"

Найди подходящие посты и ответь в соответствии с правилами.
""".strip()


class OpenRouterClient:
    def __init__(self, api_key=OPENROUTER_API_KEY, model=OPENROUTER_MODEL):
        self.api_key = api_key
        self.model = model
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def ask(self, system_prompt, user_prompt, model=None) -> str:
        model = model or self.model

        try:
            response = requests.post(
                url=OPENROUTER_API_URL,
                headers=self.headers,
                data=json.dumps({
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "reasoning": {"enabled": True}
                }),
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()
            print("OpenRouter raw response:", data)

            choices = data.get("choices")
            if not choices:
                raise Exception(f"Некорректный ответ AI‑сервиса: {data}")

            message = choices[0].get("message") if isinstance(choices, list) else None
            if not message:
                raise Exception(f"Некорректная структура choices: {choices}")

            content = message.get("content")
            if not content:
                raise Exception(f"В ответе нет content: {message}")

            return content.strip()

        except requests.exceptions.Timeout:
            raise Exception("AI‑сервис не ответил вовремя (timeout)")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ошибка запроса к AI‑сервису: {e}")


class AiSearchService:
    """Хранит ссылку на текущую стратегию и использует её для выбора вопросов."""
    def __init__(self, strategy=None):
        self.strategy = strategy or LastNQuestionsStrategy(30)
        self.llm_client = OpenRouterClient()

    def set_strategy(self, strategy):
        self.strategy = strategy

    def search(self, user_query: str) -> AiSearchResult:
        user_query = (user_query or "").strip()
        if not user_query:
            return AiSearchResult(
                error="Пустой запрос",
                question_ids=[],
            )

        try:
            questions = list(self.strategy.get_questions(user_query))
            question_ids = [q.id for q in questions]
            context = build_context(questions)
            if context is None:
                context = ""

            if not context.strip():
                return AiSearchResult(
                    error="Подходящих постов не найдено.",
                    question_ids=[],
                )

            user_prompt = make_user_prompt(user_query, context)
            answer = self.llm_client.ask(SYSTEM_PROMPT, user_prompt)

            return AiSearchResult(
                answer=answer,
                error=None,
                question_ids=question_ids,
            )

        except Exception as e:
            print("AI search exception:", repr(e))
            return AiSearchResult(
                error=f"Ошибка при обращении к ИИ: {e}",
                question_ids=[],
            )