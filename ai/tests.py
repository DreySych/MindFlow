import json
import datetime
from django.utils import timezone
from unittest import mock
from django.test import TestCase, Client
from django.urls import reverse
from questions.models import Question, Comment, Answer
from users.models import User
from ai.strategies import AllQuestionsStrategy, LastNQuestionsStrategy
from ai.services import AiSearchService, AiSearchResult, AskOllamaClient


class StrategyTests(TestCase):
    """ Тесты стратегий выбора вопросов. """

    def setUp(self):
        self.user = User.objects.create(
            username="tester",
            email="tester@test.com",
            password="12345",
            sex=1,
            reputation=0,
            role="user",
            registration_date=datetime.date.today(),
        )
        self.q1 = Question.objects.create(
            title="Первый вопрос",
            description="Описание 1",
            author=self.user,
            rating=0,
            images='',
            embedding='',
            creation_date=timezone.now() - datetime.timedelta(days=3)
        )
        self.q2 = Question.objects.create(
            title="Второй вопрос",
            description="Описание 2",
            author=self.user,
            rating=0,
            images='',
            embedding='',
            creation_date=timezone.now() - datetime.timedelta(days=2)
        )
        self.q3 = Question.objects.create(
            title="Третий вопрос",
            description="Описание 3",
            author=self.user,
            rating=0,
            images='',
            embedding='',
            creation_date=timezone.now() - datetime.timedelta(days=1)
        )

    def test_all_questions_strategy_returns_all(self):
        strategy = AllQuestionsStrategy()
        qs = list(strategy.get_questions("любой запрос"))

        self.assertEqual(len(qs), 3)
        self.assertCountEqual(
            [q.id for q in qs],
            [self.q1.id, self.q2.id, self.q3.id],
        )

    def test_last_n_questions_strategy_respects_order(self):
        """ Проверяем, что LastNQuestionsStrategy сортирует по убыванию creation_date. """
        strategy = LastNQuestionsStrategy(n=10)
        qs = list(strategy.get_questions("любой запрос"))

        # Ожидаем, что первые три — в порядке q3, q2, q1
        self.assertGreaterEqual(len(qs), 3)
        self.assertEqual(qs[0].id, self.q3.id)
        self.assertEqual(qs[1].id, self.q2.id)
        self.assertEqual(qs[2].id, self.q1.id)


class FakeOllamaClient(AskOllamaClient):
    """ Фейковый клиент Ollama для тестов: не делает реальных HTTP‑запросов. """

    def __init__(self):
        self._client = None

    def ask(self, system_prompt, user_prompt, model="qwen3:0.6b"):
        return "Фейковый ответ от ИИ для теста"


class AiSearchServiceTests(TestCase):
    """ Тесты сервиса AiSearchService. Внешнее API (Ollama) заменяем на FakeOllamaClient. """

    def setUp(self):
        self.user = User.objects.create(
            username="tester",
            email="tester@test.com",
            password="12345",
            sex=1,
            reputation=0,
            role="user",
            registration_date=datetime.date.today(),
        )
        self.q = Question.objects.create(
            title="Вопрос про сов",
            description="Описание про сов",
            author=self.user,
            rating=0,
            images='',
            embedding='',
            creation_date=timezone.now()
        )
        self.comment = Comment.objects.create(
            text="Комментарий к вопросу",
            author=self.user,
            question=self.q,
            rating=0,
            creation_date=timezone.now()
        )
        self.answer = Answer.objects.create(
            answer="Ответ к комментарию",
            author=self.user,
            comment=self.comment,
            rating=0,
            creation_date=timezone.now()
        )

    def make_service(self):
        service = AiSearchService(LastNQuestionsStrategy(n=10))
        service.llm_client = FakeOllamaClient()
        return service

    def test_search_empty_query_returns_error(self):
        service = self.make_service()
        result = service.search("")
        self.assertIsInstance(result, AiSearchResult)
        self.assertEqual(result.query, "")
        self.assertIsNone(result.answer)
        self.assertEqual(result.error, "Пустой запрос")

    def test_search_builds_context_and_calls_llm(self):
        service = self.make_service()
        result = service.search("совы")
        self.assertIsNone(result.error)
        self.assertEqual(result.answer, "Фейковый ответ от ИИ для теста")
        self.assertEqual(result.query, "совы")

    def test_search_when_no_questions_in_context(self):
        Question.objects.all().delete()
        service = self.make_service()
        result = service.search("совы")
        self.assertIsNone(result.answer)
        self.assertEqual(result.error, "Подходящих постов не найдено.")


class AiSearchApiViewTests(TestCase):
    """ Тесты view ai_search_api с использованием Django test client. """

    def setUp(self):
        self.client = Client()

    def test_ai_search_api_rejects_non_post(self):
        url = reverse("ai_search_api")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_ai_search_api_bad_json(self):
        url = reverse("ai_search_api")
        response = self.client.post(
            url,
            data="not json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content.decode("utf-8"))
        self.assertIn("error", data)

    @mock.patch("ai.views.service")
    def test_ai_search_api_success(self, mock_service):
        url = reverse("ai_search_api")
        mock_result = AiSearchResult(
            query="совы", answer="Ответ от сервиса", error=None)
        mock_service.search.return_value = mock_result

        response = self.client.post(
            url,
            data=json.dumps({"q": "совы"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data["answer"], "Ответ от сервиса")

    @mock.patch("ai.views.service")
    def test_ai_search_api_service_error(self, mock_service):
        url = reverse("ai_search_api")
        mock_result = AiSearchResult(
            query="совы", answer=None, error="Ошибка сервиса")
        mock_service.search.return_value = mock_result

        response = self.client.post(
            url,
            data=json.dumps({"q": "совы"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(data["error"], "Ошибка сервиса")
