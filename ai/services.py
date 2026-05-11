from dataclasses import dataclass
import ollama
from .strategies import SearchStrategy, LastNQuestionsStrategy
from typing import Optional

ollama_client = ollama.Client(host="http://127.0.0.1:11434")

SYSTEM_PROMPT = """Ты — ассистент для работы с постами и комментариями на русском языке.

Правила:
1. Отвечай строго на основе предоставленного списка постов и комментариев.
2. Не добавляй информацию из собственных знаний — используй только данные из запроса.
3. Если релевантных постов или комментариев нет, явно сообщи: "Подходящих постов не найдено."
4. Ответы должны быть краткими, конкретными и по существу.
5. Все ответы — только на русском языке.
6. Не используй вводные фразы типа "На основе предоставленных данных..." — сразу переходи к сути.

Формат ответа: прямой, фактический, без домысливания."""


@dataclass
class AiSearchResult:
    query: str
    answer: Optional[str] = None
    error: Optional[str] = None


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


class AskOllamaClient:
    """ Упрощённый интерфейс для работы с ollama.сlient. """

    def __init__(self, client):
        self._client = client

    def ask(self, system_prompt, user_prompt, model="qwen3:1.7b"):
        """ Отправляет запрос к LLM и возвращает текстовый ответ. """
        response = self._client.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response["message"]["content"].strip()


class AiSearchService:
    """ Хранит ссылку на текущую стратегию и использует её для выбора вопросов. """
    def __init__(self, strategy):
        # по умолчанию — только последние N вопросов
        self.strategy = strategy or LastNQuestionsStrategy(30)
        self.llm_client = AskOllamaClient(ollama_client)

    def set_strategy(self, strategy):
        """ Позволяет переключать стратегию. """
        self.strategy = strategy

    def search(self, user_query):
        if not user_query.strip():
            return AiSearchResult(query=user_query, error="Пустой запрос")

        try:
            questions = self.strategy.get_questions(user_query)
            context = build_context(questions)

            if not context.strip():
                return AiSearchResult(
                    query=user_query,
                    error="Подходящих постов не найдено.",
                )

            user_prompt = make_user_prompt(user_query, context)
            answer = self.llm_client.ask(SYSTEM_PROMPT, user_prompt)
            return AiSearchResult(query=user_query, answer=answer)
        except Exception as e:
            return AiSearchResult(query=user_query, error=f"Ошибка при обращении к ИИ: {e}")
